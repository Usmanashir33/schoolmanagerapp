from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch


from academics.models import Subject,ClassRoom

from .utils import build_student_records_workbook , decript_scores_from_workbook
from .tasks import generate_report_and_position
from .utils import build_student_character_workbook,decript_skills_from_workbook
from .models import  *
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from school.models import School
from student.models import Student
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response
from rest_framework import status

from . serializers import *
from django.core.cache import cache

class TeacherFetchResultBatchView(APIView):
    def get(self, request,school_id,session_id, term_id):
        try :
            valid_school = School.objects.filter(id=school_id).exists()
            if not valid_school :
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            cache_key = f"results_{school_id}_{session_id}_{term_id}_teacher_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            batches = ResultBatch.objects.filter(
                Q(class_room__school_id = school_id,session_id=session_id,term_id=term_id) &
                Q(class_room__teaching_assignments__teacher__user_id = request.user.id)
            ).select_related(
                'class_room','subject','teacher','session','term'
            ).order_by('id').distinct('id')
            if not batches :
                return Response({"success": 'data not found'}, status=status.HTTP_200_OK)
            serializer = ResultBatchReadListSerializer(batches, many=True).data 
            
            resp =  {"success": "", "filteredBatches": serializer}
            try :
                cache.set(cache_key,resp,timeout=60*5) # Cache for 3 minutes)
            except:
                pass
            return Response( 
                   resp,
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)

class TeacherStudentsSkillsUpsertOrGetView(APIView):
    # permission_classes=[HasSchoolPermission]
    # permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS]

    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            serializer = StudentCharAndSkillsUpsertSerializer(data=request.data)
            if serializer.is_valid():
                b = serializer.save()
                batch = CharacterBatch.objects.select_related(
                    "class_room",
                    "term",
                    "session",
                    "school"
                ).prefetch_related(
                    "charAndSkills__student"
                ).get(id=b.id)

                if not batch:
                    return Response({"error": 'enternal server error'}, status=status.HTTP_200_OK)
               
                data = SkillBatchReadDetailSerializer(batch).data 
                return Response( 
                    {"success": "Skills updated.", "currentSkills": data},
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
    
    def get(self, request,school_id, session_id, term_id):
        try :
            cache_key = f"charresults_{school_id}_{session_id}_{term_id}_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            batches = valid_school.batch_skills.filter(
                session_id = session_id,
                term_id = term_id
            )
            batches = CharacterBatch.objects.filter(
                Q(class_room__school_id = school_id,session_id=session_id,term_id=term_id) &
                Q(class_room__form_teacher__user_id = request.user.id)
            ).select_related(
                'class_room','session','term'
            ).order_by('id').distinct('id')
            if not batches :
                return Response({"success":'data not found'},status=status.HTTP_200_OK)
            serializer = SkillBatchReadListSerializer(batches, many=True).data 
            resp ={"success": "Skills fetched successfully.", "filteredCharAndSkills": serializer}
            try : 
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response( 
                    resp,
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class TeacherReportRecordListAPIView(APIView):
     
    def get(self, request,school_id,session_id,term_id) :
        try :
            cache_key = f"reportrecords_{session_id}_{term_id}_teacher_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            reports = ReportRecord.objects.filter(
                school_id = school_id,
                session_id = session_id, 
                term_id = term_id,
              )
           
            if not reports :
                return Response({"success": "Reports not found"}, status=status.HTTP_200_OK)
            
            serializer = ReportSerializer(reports,many=True)
            resp = {"success": "Records","reportRecords" :  serializer.data}
            try : 
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response( 
                    resp ,
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class TeacherReportSheetListAPIView(APIView):
    def get(self, request,school_id,session_id,term_id,class_id) :
        try :
            cache_key = f"reportsheets_{session_id}_{term_id}_{class_id}_teacher_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            reports = ReportSheet.objects.filter(
                session_id = session_id, 
                term_id = term_id,
                class_room__id = class_id,
                class_room__form_teacher__user_id = request.user.id 
              ).prefetch_related('student').order_by('position')
            
            # we will include scores in the report for subjects 
            scores = StudentResult.objects.filter(
                batch__session__id = session_id,
                batch__term__id = term_id,
                batch__class_room__id = class_id,
                batch__class_room__form_teacher__user_id = request.user.id 
            )
            
            skills = StudentCharacterSkill.objects.filter(
                batch__session__id = session_id,
                batch__term__id = term_id,
                batch__class_room__id = class_id,
                batch__class_room__form_teacher__user_id = request.user.id 
            )
            
            if not reports or not scores :
                return Response({"success": "Reports not found"}, status=status.HTTP_200_OK)
            
            serializer = ReportSheetListSerializer(reports,many=True,context={"scores":scores,"skills":skills})
            resp = {"success": "Reports","reportSheets" :  serializer.data}
            try : 
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response( 
                    resp ,
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
class TeacherReportSheetDetailAPIView(APIView):
    def get(self, request,school_id,session_id,term_id,class_id,student_id) :
        try :
            cache_key = f"reportsheet_{session_id}_{term_id}_{class_id}_{student_id}_teacher_{request.user.id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass 
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            student = Student.objects.filter(
                school_id = school_id,
                id = student_id
            ).prefetch_related(
                Prefetch(
                    "skills",
                    queryset=StudentCharacterSkill.objects.filter(
                        batch__session_id = session_id,
                        batch__term_id = term_id,
                        batch__class_room_id = class_id,
                    ).select_related("batch")
                ),
                Prefetch(
                    "results",
                    queryset = StudentResult.objects.filter(
                        batch__session_id = session_id, 
                        batch__term_id = term_id,
                        batch__class_room_id = class_id,
                        ).select_related("batch"),
                ),
                Prefetch(
                    "report_sheets",
                    queryset=ReportSheet.objects.filter(
                        session_id = session_id, 
                        term_id = term_id,
                        class_room__id = class_id,
                    ).select_related('class_room','term','session'),
                    to_attr="report_sheet",
                ),
            ).first()
            report = next(iter(student.report_sheet), None)
            
            if not student or not report:
                return Response({"success": "Report not found"}, status=status.HTTP_200_OK)
                
            # we will include scores and skills in the report for subjects  and characters 
            scores = student.results.all()
            skills = student.skills.first()
            
            serializer = ReportSheetDetailSerializer(report,context={"scores":scores,"skills":skills})
            resp = {"success": "Report","reportSheet" :  serializer.data}
            try : 
                cache.set(cache_key,resp,timeout=5*60)
            except :
                pass
            return Response( 
                    resp ,
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class TeacherResultBatchUpsertView(APIView):
    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
                
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)

            serializer = ResultBatchUpsertSerializer(data=request.data, context={ "school": valid_school})

            if serializer.is_valid():
                batch = serializer.save()
                if not batch:
                    return Response({"error": 'enternal server error'}, status=status.HTTP_200_OK)
                data = ResultBatchReadSerializer(batch).data
                return Response( 
                    {"success": "Results uploaded successfully.", "currentBatch": data},
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class TeacherBatchManageAPIView(APIView) : 
    
    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            batch_id = request.data.get("batch")
            action = request.data.get("action",None) # LOCKING,SUBMISSION
            target = request.data.get("target") # Options CHAR | RESULT
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            batch = ResultBatch.objects.filter(
                    id = batch_id,
                    class_room__teaching_assignments__teacher__user_id = request.user.id
                ).first() if target == "RESULT" else  CharacterBatch.objects.filter(
                    id = batch_id,
                    class_room__teaching_assignments__teacher__user_id = request.user.id
                ).first() if target == "CHAR" else None
           
            if not batch :
                return Response({"error": "Invalid Batch"}, status=status.HTTP_200_OK)
                
            #  lock or unlock 
            if action == 'LOCKING' :
                batch.is_locked = not batch.is_locked
                
            if action == 'SUBMISSION' :
                batch.on_submit = True # teacher cannot reject it 
                
                if not batch.on_submit : # the batch is rejected
                    batch.approved = False
                    batch.is_locked = False
                # check if batch is completed 
                else :
                    batch.is_locked = True
                    if not  batch.status == "COMPLETE" :
                        return Response({"error": "It must be completed first!"}, status=status.HTTP_200_OK)
                
            batch.save()
            
            sta = "Locked" if batch.is_locked else "Unlocked"
            uiFieldName = "manageResults" if  target == "RESULT" else "manageSkills" if target == "CHAR" else None 
            
            b = ResultBatchReadSerializer(batch).data if  target == "RESULT" else SkillBatchReadDetailSerializer(batch).data if target == "CHAR" else None 
            mapped = {
                "id":b['id'],
                "is_locked":b['is_locked'] ,
                "isLocked":b['is_locked'] ,
                "on_submit":b['on_submit'] ,
                "approved":b["approved"],
                "status":b["status"],
                "lastUpdated":b["lastUpdated"]
            }
            return Response( 
                    {"success": f"Results {sta} successfully.", uiFieldName: mapped},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
class TeacherUploadScoresAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        try :
            file = request.FILES.get("file")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            
            if not file :
                return Response({"error": "No file uploaded"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            pin = request.data.get("pin")
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            # validate teacher 
            cls = ClassRoom.objects.filter(id=class_id,school_id=school_id,teaching_assignments__teacher__user_id = request.user.id).first()
            if not cls :
                return Response({"error": "Invalid Class Selection"}, status=status.HTTP_200_OK)
            students = Student.objects.filter(
                class_rooms__class_room__id=class_id,
                class_rooms__status__in=["active", "enrolled"],
            ).distinct()
            
            result_data, error = decript_scores_from_workbook(file,request,students)
            if error :
                return Response({"error": error }, status=status.HTTP_200_OK)
            
            serializer = ResultBatchUpsertSerializer(data=result_data,context={ "school": valid_school})
            if serializer.is_valid():
                batch = serializer.save()
                if not batch:
                    return Response({"error":'enternal server error'}, status=status.HTTP_200_OK)
                data = ResultBatchReadSerializer(batch).data
                return Response( 
                    {"success": "Results uploaded successfully.", "currentBatch": data},
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
class TeacherUploadSkillAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try :
            file = request.FILES.get("file")
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_200_OK)
            
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).prefetch_related('class_rooms')  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            #validate the request user is the classform master
            cls = valid_school.class_rooms.filter(id=class_id,form_teacher__user_id = request.user.id).first()
            if not cls : 
                return Response({"error": "Invalid Class Selection"}, status=status.HTTP_200_OK)
            
            students = Student.objects.filter(
                class_rooms__class_room__id=class_id,
                class_rooms__status__in=["active", "enrolled"],
                school_id = school_id ,
            ).distinct().order_by("-joined_at")
            
            result_data, error = decript_skills_from_workbook(file,request,students)
            if error :
                return Response({"error": error }, status=status.HTTP_200_OK)
            
            serializer = StudentCharAndSkillsUpsertSerializer (data=result_data)
            if serializer.is_valid():
                batch = serializer.save()
                if not batch:
                    return Response({"error": 'enternal server error'}, status=status.HTTP_200_OK)
                data = SkillBatchReadDetailSerializer(batch).data
                return Response( 
                    {"success": "Skills uploaded", "currentSkills": data},
                    
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class TeacherStudentsSkillsUpsert(APIView):
    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id) 
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            # validate user belongs to the class form teacher or subject teacher
            cls = ClassRoom.objects.get(
                Q(teaching_assignments__teacher__user_id = request.user.id),
                school_id = school_id,
                id = request.data.get("class_room")
            ) or None
            if not cls :
                return Response({"error": "You are not authorized to perform this action"}, status=status.HTTP_200_OK)
            
            serializer = StudentCharAndSkillsUpsertSerializer(data=request.data)
            if serializer.is_valid():
                b = serializer.save()
                batch = CharacterBatch.objects.select_related(
                    "class_room",
                    "term",
                    "session",
                    "school"
                ).prefetch_related(
                    "charAndSkills__student"
                ).get(id=b.id)

                if not batch:
                    return Response({"error": 'enternal server error'}, status=status.HTTP_200_OK)
               
                data = SkillBatchReadDetailSerializer(batch).data 
                return Response( 
                    {"success": "Skills updated.", "currentSkills": data},
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
    
