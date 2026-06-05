from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache

# views.py or any view file
from core.emails.email_templates.emails import generate_school_update_email,generate_school_delete_email
from core.formatters import format_serializer_errors
from core.tasks import send_html_email,send_ordinary_sms
from core.permissions import DirectorUserPermission 
from core.serializers import DirectorSchoolSerializer 
from core.custom_pegination import CustomPagination50

from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser

from student.models import Student, StudentClassEnrollment
from student.serializers import StudentDetailSerializer

from school.models import School,ActivityLog
from school.models import School,Session

from school.serializers import SchoolSettingsSerializer,ActivityLogSerializer
from school.models import School ,SchoolDeleteRequest
from school.permissions import HasSchoolPermission, SchoolPermissions
from school.tasks import SchoolServices


from .serializers import *
from .models import *
from .utils import ClassRoomServices
from .tasks import promote_students_task 


#==================================================================================================            
#                                       ACADEMIC SETTINGS                           
#==================================================================================================

class DirectorAcademicSettingsView (APIView) :
    parser_classes =[MultiPartParser,FormParser]
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS]
    
    def put(self, request, school_id) :
        try:
            # validate director actions 
            pin = request.data.get('pin')
            if not request.user.pins.checkPin(pin) :
                return Response({"error" : "Incorrect PIN"}, status=status.HTTP_200_OK)
            school = School.objects.filter(id=school_id).first()  #.exists()
            if not school: 
                return Response({"error": "Invalid School"}, status=status.HTTP_200_OK)
            
            serializer = SchoolSettingsSerializer(school, data = request.data, partial=True,context = {"request":request})
            # by checking  directord pin 
            if serializer.is_valid() : 
                serializer.save()  
                normalized_data = DirectorSchoolSerializer(serializer.instance).data
                 # send the email to director
                try:    
                    html_content = generate_school_update_email(
                        school.director.full_name , 
                        school.name, 
                    )
                    send_html_email.delay(
                        subject="School Account Updated" ,
                        to_email=[school.director.email,school.email] , 
                        html_content=html_content
                    )
                except Exception :
                    pass 
                return Response({"success":"school updated successfully", "updated_school": normalized_data}, status=status.HTTP_200_OK)
            return Response({'error': 'Updated data meybe not available change'}, status=status.HTTP_200_OK)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK)
    
    def post(self, request,school_id): # delting the school request 
        try:
            director = request.user.director
            
            # ============= required fields ==============
            pin = request.data.get('pin')
            reason  = request.data.get('reason')
            action = request.data.get("action")
            
            if action != "delete" :
                return Response({"error": "invalid action"}, status=status.HTTP_200_OK)
                
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            school = School.objects.filter(director_id = director.id, id=school_id).first()  #.exists()
            if not school:
                return Response({"error": "school not Found"}, status=status.HTTP_200_OK)
            
            # craete delte request here 
            if school.delete_requests :
                school.on_delete_request =True
                school.save()
                return Response({"success": "school delete in progress",
                                 "details" :f"R-{school.delete_requests.days_remain()}" }, status=status.HTTP_200_OK) 
            del_request = SchoolDeleteRequest.objects.create( 
                reason = reason, school = school
            )
            del_request.save() 
            # send the email to director
            try:    
                html_content = generate_school_delete_email(
                    school.director.full_name,
                    school.name,
                )
                send_html_email.delay(
                    subject="❌ School Account Deleted",
                    to_email=[school.director.email,school.email],
                    html_content=html_content)
            except: 
                pass
            return Response({"success":"school delete request submitted successfully",'school': DirectorSchoolSerializer(school).data},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({"error":"server error"},status=status.HTTP_200_OK) 
        
class ClassEnrollmentView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def post(self, request):
        try :
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school")
            
            target_class_id = request.data.get("targetClassId")
            students_ids = request.data.get("studentIds")
            
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).prefetch_related('students').first()
            if not valid_school:
                return Response({"error": "Invalid school  Entry"}, status=status.HTTP_200_OK)
            
             #--------------- end  validate director actions -------------------
            if not all([target_class_id,students_ids]):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_200_OK
                )
            
            to_class = ClassRoom.objects.get(
                id=target_class_id,section__school__id = school_id 
            ) or None
            # implement transfer logic 
            if not to_class :
                return Response({"error": "Invalid class selection"}, status=status.HTTP_200_OK)  
            
            # prevent duplication
            students = valid_school.students.filter(id__in=students_ids).exclude(
                Q(class_rooms__class_room__id = target_class_id) & Q(class_rooms__status__in = ['active','enrolled'])
            ).all()
            if not students :
                return Response({"error": "Invalid students Selection"}, status=status.HTTP_200_OK)  
            
            ClassRoomServices.enroll_students(
                students,
                to_class=to_class,
            )
            
            # get latets data 
            cls = ClassRoom.objects.filter(
                id=to_class.id
                ).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
            ).first()
            serializer = ClassRoomDetailSerializer(cls).data
            return Response({
                "success": f"Student enrolled to {to_class.name} successfully",
                "enrolled_classroom": serializer
            }, status=status.HTTP_200_OK )
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)   

class ClassTransferView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def put(self, request):
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school")
            
            target_class_id = request.data.get("target_class_id")
            current_class_id = request.data.get("current_class_id")
            students_ids = request.data.get("transfer_students_ids")
            
            #--------------- end  validate director actions -------------------
            if not all([school_id, target_class_id, students_ids ]):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_200_OK
                )
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).prefetch_related('students').first() 
            if not valid_school:
                return Response({"error": "Invalid school Entry"}, status=status.HTTP_200_OK)
            
            from_class = ClassRoom.objects.filter(id = current_class_id,section__school_id=school_id).first()
            to_class = ClassRoom.objects.filter(id=target_class_id,section__school_id=school_id).first()  
            if not to_class or not from_class  :
                return Response({"error": "Invalid class / Already enrolled"}, status=status.HTTP_200_OK)  
            
            # prevent duplication and make sure all students are in current class and not in the target class
            students_active_in_target = valid_school.students.filter(
                id__in=students_ids,
                class_rooms__class_room_id=target_class_id,
                class_rooms__status__in=["active", "enrolled"]
            ).values_list("id",flat=True)
            
            students = valid_school.students.filter(
                id__in=students_ids,
                class_rooms__class_room_id=current_class_id,
                class_rooms__status__in=["active", "enrolled"]
            ).exclude(
                id__in = students_active_in_target
            ).distinct()
                        
            if  not students :
                return Response({"error": "Invalid students Selection"}, status=status.HTTP_200_OK)  
            
            ClassRoomServices.transfer_students(
                students,
                to_class=to_class,
                from_class=from_class,
            )   
            # get latets data 
            clses = ClassRoom.objects.filter(
                id__in=[current_class_id,target_class_id]
                ).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
            )
            currentClass = clses.filter(id=current_class_id).first()
            toClass = clses.filter(id=target_class_id).first()
            return Response({
                    "success": f"Students Trasfered to {to_class.name} successfully",
                    "from_class": ClassRoomDetailSerializer(currentClass).data,
                    "to_class": {"studentsCount": toClass.studentsCount,'id':toClass.id,'name':toClass.name}
                }, status=status.HTTP_200_OK )
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)   
class ClassSubjectManagerView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def post(self, request) :
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get("school")
            class_id = request.data.get("classId")
            assignment_mappings = request.data.get("mappings")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).prefetch_related('subjects','teachers').first() 
            if not valid_school:
                return Response({"error": "Invalid school Entry"}, status=status.HTTP_200_OK)
            
            classroom = ClassRoom.objects.filter(
                id = class_id ,section__school_id=school_id
            ).prefetch_related(
                'teaching_assignments'
            ).first()
            if not classroom :
                return Response({"error": "Invalid class"}, status=status.HTTP_200_OK)
            
            subject_ids = [m.get("subjectId") for m in assignment_mappings]
            teacher_ids = [m.get("teacherId") for m in assignment_mappings]

            existing_subject_ids = set(
                classroom.teaching_assignments
                .filter(subject__id__in=subject_ids)
                .values_list("subject__id", flat=True)
            )

            subjects = {
                sub.id: sub
                for sub in valid_school.subjects.filter(
                    id__in=subject_ids
                ).exclude(
                    id__in=existing_subject_ids
                )
            }

            teachers = {
                teacher.id: teacher
                for teacher in valid_school.teachers.filter(
                    id__in=teacher_ids
                )
            }

            valid_mappings = []

            for mapping in assignment_mappings:
                sub_id = mapping.get("subjectId")
                tea_id = mapping.get("teacherId")
                ready_map ={  "subject": None,  "teacher": None,}  
                            
                if not subjects.get(sub_id) :
                    continue
                ready_map["subject"] = subjects[sub_id]
                if teachers.get(tea_id):
                    ready_map["teacher"] = teachers[tea_id]

                valid_mappings.append(ready_map)
            if not valid_mappings :
                return Response({"error": "No valid subject-teacher mappings provided"}, status=status.HTTP_200_OK)

            ClassRoomServices.subjects_assign(
                school = valid_school,
                cls=classroom,
                mappings = valid_mappings,
            )   
            # get latets cls  data 
            cls = ClassRoom.objects.filter(
                id =class_id
                ).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
            ).first()
            return Response({
                    "success": f"Subjects Assigned to {cls.name} successfully",
                    "assigned_subject_class": ClassRoomDetailSerializer(cls).data,
                }, status=status.HTTP_200_OK )
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)   
    
    def put(self, request) :
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get("school")
            class_id = request.data.get("classId")
            assignment_mappings = request.data.get("mappings")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).prefetch_related('subjects','teachers').first() 
            if not valid_school:
                return Response({"error": "Invalid school Entry"}, status=status.HTTP_200_OK)
            
            classroom = ClassRoom.objects.filter(
                id = class_id ,section__school_id=school_id
            ).prefetch_related(
                'teaching_assignments'
            ).first()
            if not classroom :
                return Response({"error": "Invalid class"}, status=status.HTTP_200_OK)
            
            subject_ids = [m.get("subjectId") for m in assignment_mappings]
            teacher_ids = [m.get("teacherId") for m in assignment_mappings]

            assignments = {
                assignment.subject.id : assignment
                for assignment in classroom.teaching_assignments.filter(
                    subject__id__in=subject_ids
                ).distinct()
            }

            teachers = {
                teacher.id: teacher
                for teacher in valid_school.teachers.filter(
                    id__in=teacher_ids
                )
            }

            valid_assignments = []

            for mapping in assignment_mappings:
                sub_id = mapping.get("subjectId")
                tea_id = mapping.get("teacherId")
                ready_map ={  "assignment": None,  "teacher": None,}  
                            
                if not assignments.get(sub_id) :
                    continue
                ready_map["assignment"] = assignments[sub_id]
                if teachers.get(tea_id) :
                    ready_map["teacher"] = teachers[tea_id]

                valid_assignments.append(ready_map)
            if not valid_assignments :
                return Response({"error": "No valid subject-teacher mappings provided"}, status=status.HTTP_200_OK)

            ClassRoomServices.subjects_re_assign(
                school = valid_school,
                mappings = valid_assignments,
            )   
            # get latets cls  data 
            cls = ClassRoom.objects.filter(
                id =class_id
                ).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
            ).first()
            data= ClassRoomDetailSerializer(cls).data
            return Response({
                    "success": f"Subjects Ressigned to {cls.name} successfully",
                    "reassigned_subject_class": {
                        "id":data['id'],
                        'subjects':data['subjects'],
                        'tachersCount' :data['teachersCount'],
                        'teachers':data['teachers'],
                    }
                }, status=status.HTTP_200_OK )
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)   
         
    def delete(self, request,school_id,class_id,subject_id,pin) :
        try:
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).prefetch_related('subjects','teachers').first() 
            if not valid_school:
                return Response({"error": "Invalid school Entry"}, status=status.HTTP_200_OK)
            
            classroom = ClassRoom.objects.filter(
                id = class_id ,section__school_id=school_id
            ).prefetch_related(
                'teaching_assignments'
            ).first()
            if not classroom :
                return Response({"error": "Invalid class"}, status=status.HTTP_200_OK)
            
            
            assignment = classroom.teaching_assignments.filter(
                subject__id = subject_id
                ).first()
            if not assignment :
                return Response({"error": "No valid subject-teacher "}, status=status.HTTP_200_OK)
            
            #.................DELETION ACTION ................
            assignment.delete()
           
            # get latets cls  data 
            cls = ClassRoom.objects.filter(
                id =class_id
                ).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
            ).first()
            data= ClassRoomDetailSerializer(cls).data
            return Response({
                    "success": f"Subject deleted from {cls.name} successfully",
                    "delassigned_subject_class": {
                        "id":data['id'],
                        'subjects':data['subjects'],
                        'tachersCount' :data['teachersCount'],
                        'teachers':data['teachers'],
                    }
                }, status=status.HTTP_200_OK )
                
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)   
         
class DirectorClassPromotionView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def post(self, request):
        # try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school")
            session_id = request.data.get("sessionId")
            mappings = request.data.get("mappings")
            
            #--------------- validate director actions -------------------
            director = request.user.director 
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(director_id = director.id, id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            session = Session.objects.filter( id=session_id, school=valid_school ).first() 
            if not session :
                return Response({"error": "Invalid session"}, status=status.HTTP_200_OK) 
            
            promotion_log = PromotionLog.objects.create(
                promoted_by = request.user ,
                school = valid_school ,
                session = session ,
                total_batches = len(mappings),
                mappings = mappings ,
            )
            if promotion_log.id :
                resp = promote_students_task.delay(mappings,session_id,promotion_log.id)
                if resp :
                    serializer = PromotionLogSerializer(promotion_log).data
                    return Response({ 
                            "success": f"Students promotion submitted",
                            "promotion_log":serializer,
                            "task_id":str(resp.id) ,
                        }, status=status.HTTP_200_OK )
                else :
                    return Response({
                        "error": f"Students Promotion failed",
                        "promotion_log":serializer.data
                    }, status=status.HTTP_200_OK )
            else :
                return Response({
                    "error": f"Promotion Log Failed",
                }, status=status.HTTP_200_OK )
                    
        # except Exception as e :
            # return Response({"error": "server error"}, status=status.HTTP_200_OK)   
            
class AcademicDetailsView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS] 
    
    def get(self, request,school_id,academic_item,item_id):   ## add new academic data
        try:
           
            valid_school = School.objects.filter( id=school_id).prefetch_related('sections', 'sections__classrooms','subjects').first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            # find catched data before querying the database
            cache_key = f"academics_{school_id}_{academic_item}_{item_id}"
            cached_response = cache.get(cache_key)
            if cached_response :
                return Response(cached_response, status=status.HTTP_200_OK)
            
            #---------------------------SECTION -------------------
            if academic_item == "sections":
                section= valid_school.sections.filter(id=item_id).first()
                if not section :
                    return Response({"error": "Section not found"}, status=status.HTTP_200_OK)
                serializer = SchoolSectionDetailSerializer(section)
                resp = {
                    "success": "Section",
                    "section_details": serializer.data
                }
                cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                
                return Response(resp, status=status.HTTP_200_OK)
                    
            #--------------------------- CLASSROOM -------------------
            if academic_item == "classrooms" :
                
                classroom = ClassRoom.objects.filter(id=item_id,section__school__id = school_id).prefetch_related(
                    'student_enrollments__student','teaching_assignments'
                ).select_related(
                    'form_teacher'
                ).annotate(
                    studentsCount=Count(
                        "student_enrollments",
                        filter=Q(
                            student_enrollments__status__in=["active", "enrolled"]
                        ),
                        distinct=True,
                    ),
                    teachersCount=Count(
                        "teaching_assignments__teacher",
                        distinct=True,
                    ),
                ).first()
                if not classroom :
                    return Response({"error": "Classroom not found"}, status=status.HTTP_200_OK)
                serializer = ClassRoomDetailSerializer(classroom).data
                resp={
                    "success": "Classroom",
                    "classroom_details": serializer 
                }
                cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                
                return Response(resp, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS -------------------
            if academic_item == "subjects":
                subject = valid_school.subjects.filter(id=item_id).first()
                if not subject :
                    return Response({"error": "Subject not found"}, status=status.HTTP_200_OK)
                serializer = SubjectDetailSerializer(subject)
                resp = {
                    "success": "Subject",
                    "subject_details": serializer.data
                }
                cache.set(cache_key,resp,timeout=60*5) # Cache for 5 minutes)
                
                return Response(resp, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
class AcademicView(APIView):
    permission_classes = [HasSchoolPermission]
    required_permissions = [SchoolPermissions.CAN_MANAGE_ACADEMICS]
    
    def post(self, request,academic_item):   ## add new academic data
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter( id=school_id).prefetch_related('sections', 'subjects').first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            #---------------------------SECTION CREATION -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                if valid_school.sections and valid_school.sections.filter(name__iexact = name).first():
                    return Response({"error": "Section Name Already Exist"}, status=status.HTTP_200_OK)
                
                serializer = SchoolSectionCreateUpdateSerializer(data=request.data)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Section created successfully",
                    "new_section": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
                    
            #---------------------------CLASSROOM CREATION -------------------
            if academic_item == "classrooms":
                # validate section 
                name = request.data.get('name')
                if ClassRoom.objects.filter(name__iexact = name,section__school__id= school_id).first():
                    return Response({"error": "Classroom Name Already Exist"}, status=status.HTTP_200_OK)
                
                serializer = ClassRoomCreateUpdateSerializer(data=request.data)
                
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Class Room created successfully",
                    "new_classroom": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS CREATION -------------------
            if academic_item == "subjects":
                # validate section 
                name = request.data.get('name')
                code = request.data.get('code')
                found_subject =  valid_school.subjects.filter(Q(name__iexact=name) | Q(code__iexact=code)).values('name','code').first()
                    
                if found_subject :
                    if found_subject.get('name').lower() == name.lower() :
                        return Response({"error": "Subject Name Already Exist"}, status=status.HTTP_200_OK)
                    if found_subject.get('code').lower() == code.lower() :
                        return Response({"error": "Subject Code Already Exist"}, status=status.HTTP_200_OK)

                serializer = SubjectCreateUpdateSerializer(data=request.data,context = {"request":request,'school_id':valid_school.id})
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Subject added successfully",
                    "new_subject": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    def put(self, request,academic_item,item_id):   ## update  
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter( id=school_id).prefetch_related('sections','subjects').first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            #---------------------------SECTION UPDATE -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                name_exist = valid_school.sections.filter(
                    name__iexact=name
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                
                section = valid_school.sections.filter(id = item_id).first()
                if not section :
                    return Response({"error": "Section not found"}, status=status.HTTP_200_OK)
                    
                serializer = SchoolSectionCreateUpdateSerializer(section, data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Section update successfully",
                    "updated_section": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
                    
            #---------------------------CLASSROOM UPDATE -------------------
            if academic_item == "classrooms":
                # validate section 
                name = request.data.get('name')
                name_exist = ClassRoom.objects.filter(
                    name=name,
                    section__school__id = valid_school.id
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                
                classroom = ClassRoom.objects.filter(id = item_id ,section__school__id = valid_school.id).first()
                if not classroom :
                    return Response({"error": "Class not exist"}, status=status.HTTP_200_OK)
                
                serializer = ClassRoomCreateUpdateSerializer(classroom,data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Classroom updated successfully",
                    "updated_classroom": serializer.data 
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
            #---------------------------CLASSROOM UPDATE form_teacher -------------------
            if academic_item == "form_teacher":
                classroom = ClassRoom.objects.filter(id = item_id ,section__school__id = valid_school.id).first()
                if not classroom :
                    return Response({"error": "Class not exist"}, status=status.HTTP_200_OK)
                t_id = request.data.get("teacherId",None)
                teacher = valid_school.teachers.filter( id = t_id ).first()
                if not teacher :
                    return Response({"error": "Teacher not exist"}, status=status.HTTP_200_OK)
                classroom.form_teacher = teacher
                classroom.save()
                
                serializer = ClassRoomCreateUpdateSerializer(classroom)
                return Response({
                    "success": "Classroom updated successfully",
                    "form_classroom": serializer.data 
                    }, status=status.HTTP_200_OK)
                
            #---------------------------SUBJECTS UPDATE--------------------
            if academic_item == "subjects":
                # validate section 
                name = request.data.get('name')
                code = request.data.get('code')
                
                subject_exists = valid_school.subjects.filter(
                        Q(name__iexact=name) | Q(code__iexact=code)
                    ).exclude(
                        id = item_id
                    ).values("name",'code').first()

                if subject_exists:
                    if subject_exists.get('name').lower() == name.lower() :
                        return Response({"error": "Subject Name Already Exist"}, status=status.HTTP_200_OK)
                    if subject_exists.get('code').lower() == code.lower() :
                        return Response({"error": "Subject Code Already Exist"}, status=status.HTTP_200_OK)

                subject = valid_school.subjects.filter(id = item_id).first()
                if not subject:
                    return Response(
                        {"error": "Subject not  exists"},
                        status=status.HTTP_200_OK
                    )
                
                serializer = SubjectCreateUpdateSerializer(subject,data=request.data,partial=True,context = {"request":request,'school_id':school_id})
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Subject Updated successfully",
                    "updated_subject": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    def delete(self, request,school_id,academic_item,item_id,pin):   ## DELETE 
        try:
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter( id=school_id).prefetch_related('sections','subjects').first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            #---------------------------SECTION UPDATE -------------------
            if academic_item == "sections":
                # validate section 
                
                section = valid_school.sections.filter(id = item_id).first()
                if not section :
                    return Response({"error": "Section not found"}, status=status.HTTP_200_OK)
                    
                if section :
                    section.delete()
                    # configuring activity log data 
                    new_log = ActivityLog.objects.create(
                        school = valid_school ,
                        user=request.user,
                        action="DELETE",
                        module="SECTION",
                        description=f"Section {'deleted'}:{item_id}-{section.name}"
                    )
                    user_room = f"room{request.user.id}"
                    log_data = ActivityLogSerializer(new_log).data
                    data = {
                        "type": "send_response1",
                        "activity_log": log_data,
                        }
                    try:
                        SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                    except :
                        pass
                    return Response({
                    "success": "Section deleted successfully",
                    "deleted_section": {'id':item_id}
                }, status=status.HTTP_200_OK)
                    
            #---------------------------CLASSROOM UPDATE -------------------
            if academic_item == "classrooms":
                # validate section 
                classroom = ClassRoom.objects.filter(id = item_id,section__school__id = valid_school.id).first()
                if not classroom :
                    return Response({"error": "Class not exist"}, status=status.HTTP_200_OK)
                
                classroom.delete()
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                        school = valid_school,
                        user=request.user,
                        action="DELETE",
                        module="CLASSROOM",
                        description=f"Classroom {'deleted'}:{item_id}-{classroom.name}"
                    )
                user_room = f"room{request.user.id}"
                log_data = ActivityLogSerializer(new_log).data
                data = {
                        "type": "send_response1",
                        "activity_log": log_data,
                        }
                try:
                        SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                except :
                        pass
                return Response({
                "success": "Classroom deleted successfully",
                "deleted_classroom": {"id":item_id}
                }, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS UPDATE-------------------
            if academic_item == "subjects":
                # validate section 

                subject = valid_school.subjects.filter(id = item_id).first()
                if not subject:
                    return Response(
                        {"error": "Subject not  exists"},
                        status=status.HTTP_200_OK
                    )
                
                subject.delete()
                # configuring activity log data 
                new_log = ActivityLog.objects.create(
                        school = valid_school,
                        user=request.user,
                        action="DELETE",
                        module="SUBJECT",
                        description=f"Subject {'deleted'}:{item_id}-{subject.name}"
                    )
                user_room = f"room{request.user.id}"
                log_data = ActivityLogSerializer(new_log).data
                data = {
                        "type": "send_response1",
                        "activity_log": log_data,
                        }
                try:
                        SchoolServices.send_activity_log.delay(destination=user_room, data=data)
                except :
                        pass
                return Response({
                    "success": "Subject deleted successfully",
                    "deleted_subject": {"id":item_id}
                }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)




