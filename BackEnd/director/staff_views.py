from django.db.models import Q

# core app
# views.py or any view file
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser,FormParser
from school.models import School 
from staff.serializers import StaffSerializer,StaffDetailSerializer
from staff.models import Staff
from section.serializers import SchoolSectionDetailSerializer
from section.models import SchoolSection
from classroom.serializers import ClassRoomDetailSerializer
from subject.serializers import SubjectDetailSerializer
from subject.models import Subject

from core.custom_pegination import CustomPagination50
from classroom.models import ClassRoom
from school.models import School


#==================================================================================================            
#                                       STAFF SECTION                           
#==================================================================================================
class DirectorAllStaffsView(APIView): #paginated request
    permission_classes = [DirectorUserPermission]
    # ---------------- GET  ALL Staff -----------------
    def get(self, request,school_id):  
        try:
            director = request.user.director 
            # validate director actions 
            valid_school  = School.objects.filter(id = school_id, director=director.id).first() 
            if not valid_school:
                return Response({"error": "Staff not found"}, status=status.HTTP_200_OK)
            # get all students 
            staffs = valid_school.staffs.all().order_by('joined_at') # all school students 
            paginator = CustomPagination50()
            staffs = paginator.paginate_queryset(staffs, request )
            serializer_data = StaffSerializer(staffs, many=True).data
            paginated_staffs = paginator.get_paginated_response(serializer_data)
            
            return Response({ 
                    "success": "School staffs",
                    "staffs_data": paginated_staffs.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorFilterStaffView(APIView):
    permission_classes = [DirectorUserPermission]
    # ---------------- SEARCH Staff -----------------
    def get(self, request,searchQuery):  
        try:
            director = request.user.director
             # validate director actions 
            searched  = Staff.objects.filter(
                Q(id__icontains = searchQuery) | Q(first_name__icontains = searchQuery) |  Q(title__icontains = searchQuery) |
                Q(last_name__icontains = searchQuery)  | Q(middle_name__icontains = searchQuery) | Q(email__icontains = searchQuery) |
                  Q(phone__icontains = searchQuery) | Q(staff_id__icontains = searchQuery)
            ).filter(school__director__id = director.id)
            
            if not searched:
                return Response({"success": "not found"}, status=status.HTTP_200_OK)
            serializer = StaffDetailSerializer(searched,many=True)
            return Response({
                    "success": "searchResults",
                    "results": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
class DirectorStaffView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]
    # ---------------- GET Staff -----------------
    def get(self, request,staff_id):  
        try:
            director = request.user.director
             # validate director actions 
            valid_staff  = Staff.objects.filter(id = staff_id, school__director=director.id).first()  #.exists()
            if not valid_staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)
            serializer = StaffSerializer(valid_staff)
            return Response({
                    "success": "staff details",
                    "staff": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
            
    def post(self, request):   ## add new staff 
        try:
            director = request.user.director
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            serializer = StaffDetailSerializer(data=request.data,context = {"request":request}) 
            if serializer.is_valid():
                serializer.save() 
                
                
                return Response({
                    "success": "staff created successfully",
                    "new_staff": serializer.data
                }, status=status.HTTP_200_OK)
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

    # ---------------- UPDATE staff -----------------
    def put(self, request,staff_id):
        try : 
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id, school__director=director.id
            ).first()
            if not staff:
                return Response({"error": "staff not found"}, status=status.HTTP_200_OK)

            serializer = StaffDetailSerializer(staff, data=request.data,partial=True,context = {"request":request})
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "success": "staff updated successfully",
                    "updated_staff": serializer.data
                }, status=status.HTTP_200_OK)
            print('serializer.errors: ', serializer.errors)
            return Response({"error": serializer.errors}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)

class DirectorStaffAdministrationView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,staff_id,request_action):
        try:
            director = request.user.director
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            print('school_id: ', school_id,staff_id)
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
             # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)

            staff = Staff.objects.filter(
                id=staff_id,
                school__director=director.id
            ).first()

            if not staff:
                return Response({"error": "Staff not found "}, status=status.HTTP_200_OK)
            serializer = StaffSerializer(staff)
            # ---------------- DELETE STAFF -----------------
            if request_action == "delete":
                staff.delete()
                return Response({
                    "success": f"Staff {request_action} successfully",
                    "del_staff": serializer.data
                }, status=status.HTTP_200_OK)
            # ---------------- SUSPEND / ACTIVATE  STAFF -----------------
            if request_action == "suspend":
                user = staff.user
                user.is_active = not user.is_active
                user.save()
                request_action = "Activated" if user.is_active else "Suspended" 
                return Response({
                    "success": f"Staff {request_action} successfully",
                    "sus_staff": serializer.data
                }, status=status.HTTP_200_OK)
        except:
            return Response({"error": "server error"}, status=status.HTTP_200_OK)
        
    # --------------------------------------------------------------------------------------------
    #                                             ACADEMICS
    # --------------------------------------------------------------------------------------------
class DirectorAcademicView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request,academic_item):   ## add new staff 
        try:
            pin = request.data.get( "pin" )
            school_id = request.data.get( "school" )
            
            director = request.user.director
            
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            #---------------------------SECTION CREATION -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                section_found = School.objects.filter(sections__name = name, id=school_id)
                if section_found :
                    return Response({"error": "Name Exist"}, status=status.HTTP_200_OK)
                serializer = SchoolSectionDetailSerializer(data=request.data)
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
                classroom_found = School.objects.filter(sections__classrooms__name = name, id=school_id)
                if classroom_found :
                    return Response({"error": "Name already exist"}, status=status.HTTP_200_OK)
                serializer = ClassRoomDetailSerializer(data=request.data)
                
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
                subject_found = School.objects.filter(
                    Q(subjects__name__iexact=name) | Q(subjects__code__iexact=code),
                    id=school_id
                ).exists()

                if subject_found:
                    return Response(
                        {"error": "Subject name or code already exists"},
                        status=status.HTTP_200_OK
                    )
                serializer = SubjectDetailSerializer(data=request.data,context = {"request":request})
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
            school_id = request.data.get( "school" )
            director = request.user.director
             #--------------- validate director actions -------------------
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
             #--------------- end  validate director actions -------------------
            
            #---------------------------SECTION UPDATE -------------------
            if academic_item == "sections":
                # validate section 
                name = request.data.get('name')
                name_exist = SchoolSection.objects.filter(
                    school=school_id,
                    name=name
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                section = SchoolSection.objects.filter(id = item_id).first()
                if not section :
                    return Response({"error": "Section not exist"}, status=status.HTTP_200_OK)
                    
                serializer = SchoolSectionDetailSerializer(section, data=request.data,partial=True)
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
                    name=name
                ).exclude(
                    id=item_id
                )
                if name_exist :
                    return Response({"error": "Section name alraedy exist"}, status=status.HTTP_200_OK)
                classroom = ClassRoom.objects.filter(id = item_id).first()
                if not classroom :
                    return Response({"error": "Class not exist"}, status=status.HTTP_200_OK)
                
                serializer = ClassRoomDetailSerializer(classroom,data=request.data,partial=True)
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Classroom updated successfully",
                    "updated_classroom": serializer.data 
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
            
            #---------------------------SUBJECTS UPDATE-------------------
            if academic_item == "subjects":
                # validate section 
                name = request.data.get('name')
                code = request.data.get('code')
                
                
                subject_exists = Subject.objects.filter(
                        school_id=school_id
                    ).filter(
                        Q(name__iexact=name) | Q(code__iexact=code)
                    ).exclude(
                        id=item_id
                    ).exists()

                if subject_exists:
                    return Response(
                        {"error": "Subject name or code already exists"},
                        status=status.HTTP_200_OK
                    )
                subject = Subject.objects.filter(id = item_id).first()
                if not subject:
                    return Response(
                        {"error": "Subject not  exists"},
                        status=status.HTTP_200_OK
                    )
                
                serializer = SubjectDetailSerializer(subject,data=request.data,partial=True,context = {"request":request})
                if serializer.is_valid() :
                    serializer.save()
                    return Response({
                    "success": "Subject Updated successfully",
                    "updated_subject": serializer.data
                }, status=status.HTTP_200_OK)
                return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e :
            return Response({"error": "server error"}, status=status.HTTP_200_OK)




