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
from .models import ResultBatch ,ReportSheet,StudentResult,StudentCharacterSkill ,CharacterBatch,ApprovalRecord
from core.formatters import format_serializer_errors
from core.permissions import DirectorUserPermission
from school.models import School
from student.models import Student
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from . serializers import *
from school.permissions import HasSchoolPermission, SchoolPermissions
from django.core.cache import cache

class ResultBatchUpsertView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [
        SchoolPermissions.CAN_MANAGE_RESULTS
    ]
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
class FetchResultBatchView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [
        SchoolPermissions.CAN_MANAGE_RESULTS
    ]
    
    def get(self, request,school_id, session_id, term_id):
        try :
            valid_school = School.objects.filter(id=school_id).exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            cache_key = f"results_{school_id}_{session_id}_{term_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            batches = ResultBatch.objects.filter(
                class_room__section__school__id = school_id,
                session_id=session_id,
                term_id=term_id
            ).select_related(
                'class_room','subject','teacher','session','term'
            )
            if not batches :
                return Response({"success": 'data not found'}, status=status.HTTP_200_OK)
                
            serializer = ResultBatchReadSerializer(batches, many=True).data 
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
class ApprovalHistoriesView(APIView):
    def get(self, request,school_id) :
        try :
            valid_school = School.objects.filter(id=school_id)
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            cache_key = f"approvals_{school_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            history = ApprovalRecord.objects.filter(school__id = school_id).order_by("-timestamp")[:50]
            serializer = ApprovalRecordSerializer(history, many=True).data 
            resp = {"success": "history fetched successfully.", "approvalHistories": serializer}
            try :
                cache.set(cache_key,resp,timeout=60*5) # Cache for 3 minutes)
            except:
                pass
            return Response( 
                    resp,
                    status=status.HTTP_200_OK )
        except Exception as e :
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
class DownloadScoreTemplateView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [
        SchoolPermissions.CAN_ADD_RESULTS
    ]
    def get(self, request, school_id, session_id, term_id ,class_id,subject_id):
        
        valid_school = School.objects.filter(id=school_id).prefetch_related(
            "classrooms",'sessions','terms','subjects'
            ).first()
        if not valid_school:
            return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
        
        students = Student.objects.filter(
            class_rooms__class_room__id=class_id,
            class_rooms__status__in=["active", "enrolled"],
        ).distinct()
        # ✅ Generate Excel
        request_data ={
            "school_id"  : school_id,
            "session_id"  : session_id,
            "term_id"  : term_id,
            "class_id"  : class_id,
            "subject_id"  : subject_id,
        }
        workbook_stream = build_student_records_workbook(
            request_data,
            students,
            max_marks = valid_school.max_marks if valid_school.max_marks else {"ca1":20,"ca2":20,"exam":60} ,
            school_name = valid_school.name,
            class_name = valid_school.classrooms.filter(id=class_id).first().name,
            term_name=valid_school.terms.filter(id=term_id).first().name,
            session_name=valid_school.sessions.filter(id=session_id).first().name,
            subject_name=valid_school.subjects.filter(id=subject_id).first().name
        )

        response = HttpResponse(
            workbook_stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = (
            'attachment; filename="score_template.xlsx"'
        )

        return response
class UploadScoresAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_ADD_RESULTS ]
    
    def post(self, request):
        try :
            file = request.FILES.get("file")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            pin = request.data.get("pin")
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
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

class DownloadSkillTemplateView(APIView):
    permission_classes = [DirectorUserPermission]

    def get(self, request, school_id, session_id, term_id ,class_id,):
        
        valid_school = School.objects.filter(id=school_id)  #.exists()
        if not valid_school:
            return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
        
        students = Student.objects.filter(
            class_rooms__class_room__id=class_id,
            class_rooms__status__in=["active", "enrolled"],
        ).distinct().order_by("joined_at")
        # ✅ Generate Excel

        request_data ={
            "school_id"  : school_id,
            "session_id"  : session_id,
            "term_id"  : term_id,
            "class_id"  : class_id,
        }
        workbook_stream = build_student_character_workbook(
            request_data,
            students,
            school_name = valid_school.first().name,
            class_name = ClassRoom.objects.filter(id=class_id,section__school__id=school_id).first().name,
            term_name=valid_school.first().terms.filter(id=term_id).first().name,
            session_name=valid_school.first().sessions.filter(id=session_id).first().name,
        )
        response = HttpResponse(
            workbook_stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            'attachment; filename="skill_template.xlsx"'
        )
        return response

class BatchManageAPIView(APIView) : 
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS ]
    
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
                    id = batch_id
                ).first() if target == "RESULT" else  CharacterBatch.objects.filter(
                    id = batch_id
                ).first() if target == "CHAR" else None
           
            if not batch :
                return Response({"error": "Invalid Batch"}, status=status.HTTP_200_OK)
                
            #  lock or unlock 
            if action == 'LOCKING' :
                batch.is_locked = not batch.is_locked
                
            if action == 'SUBMISSION' :
                batch.on_submit = not batch.on_submit
                if not batch.on_submit : # checking for  false
                    batch.approved = False
                    batch.is_locked = False
                # check if batch is comleted 
                else :
                    batch.is_locked = False
                    if not  batch.status == "COMPLETE" :
                        return Response({"error": "status must be completed first!"}, status=status.HTTP_200_OK)
                
            batch.save()
            
            sta = "Locked" if batch.is_locked else "Unlocked"
            # uiFieldName = "currentBatch" if  target == "RESULT" else "currentSkills" if target == "CHAR" else None 
            uiFieldName = "manageResults" if  target == "RESULT" else "manageSkills" if target == "CHAR" else None 
            
            b = ResultBatchReadSerializer(batch).data if  target == "RESULT" else SkillBatchReadSerializer(batch).data if target == "CHAR" else None 
            mapped = {
                "id":b['id'],
                "is_locked":b['is_locked'],
                "isLocked":b['is_locked'],
                "on_submit":b['on_submit'],
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

class BatchApproveAPIView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS]
    
    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            batch_ids = request.data.get("batchIds")
            target = request.data.get("target") # Options CHAR | RESULT
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(id=school_id).first()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            batches = ResultBatch.objects.filter(
                    id__in  = batch_ids
                ) if target == "RESULT" else  CharacterBatch.objects.filter(
                    id__in  = batch_ids
                ) if target == "CHAR" else None
           
            if not batches :
                return Response({"error": "Invalid Batches Ids"}, status=status.HTTP_200_OK)
            #  lock and approved 
            for batch in batches :
                batch.approved = not batch.approved
                # batch.save()
                if batch.approved :
                    batch.is_locked = True
                    batch.on_submit = False
                    batch.save()
            
            descriptions = [
                str(b.class_room.name) for b in batches
            ] if target == "CHAR" else [
                str(f"{b.class_room.name}_{b.subject.name}") for b in batches
            ] if target == "RESULT" else ["Not Recognized"]
            
            history = ApprovalRecord.objects.create(
                school = valid_school,
                description	 = f"Approved: {",".join(descriptions)}|{target}",
                directorName = request.user.full_name() ,	 
                batchCount = batches.count() ,	 
            )
            history_data = ApprovalRecordSerializer(history).data 
            
            sta = "Approved" if batch.is_locked else "Rejected"
            uiFieldName = "approvedResults" if  target == "RESULT" else "approvedSkills" if target == "CHAR" else None 
            if not batches :
                return Response({"success":'data not found'},status=status.HTTP_200_OK)
            data = ResultBatchReadSerializer(batches,many=True).data if  target == "RESULT" else SkillBatchReadSerializer(batches,many=True).data if target == "CHAR" else None 
            mapped = [{
                "id":b['id'],
                "is_locked":b['is_locked'],
                "isLocked":b['is_locked'],
                "on_submit":b['on_submit'],
                "approved":b["approved"],
                "status":b["status"],
                "lastUpdated":b["lastUpdated"]
                
            } for b in data ]
            return Response( 
                    {"success": f"Results {sta} successfully.", uiFieldName: mapped,"history":history_data},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
class StudentsSkillsUpsertOrGetView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS]

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
               
                data = SkillBatchReadSerializer(batch).data 
                return Response( 
                    {"success": "Skills updated.", "currentSkills": data},
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
    
    def get(self, request,school_id, session_id, term_id):
        try :
            cache_key = f"charresults_{school_id}_{session_id}_{term_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            valid_school = School.objects.filter(id=school_id).prefetch_related("batch_skills").first()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            batches = valid_school.batch_skills.filter(
                session_id = session_id,
                term_id = term_id
            )
            if not batches :
                return Response({"success":'data not found'},status=status.HTTP_200_OK)
            serializer = SkillBatchReadSerializer(batches, many=True).data 
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
class UploadSkillAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS]

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
            valid_school = School.objects.filter(id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
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
                data = SkillBatchReadSerializer(batch).data
                return Response( 
                    {"success": "Skills uploaded", "currentSkills": data},
                    
                    status=status.HTTP_200_OK
                )
            return Response({"error": format_serializer_errors(serializer.errors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)

class GenerateClassReportSheetAPIView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [ SchoolPermissions.CAN_MANAGE_RESULTS]

    def post(self, request):
        try :
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            term_id = request.data.get("term")
            session_id = request.data.get("session")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            
            valid_school = School.objects.filter(id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid School Entry"}, status=status.HTTP_200_OK)
            
            report_data = generate_report_and_position.delay(term_id,session_id,class_id,school_id)
            res = report_data.get() or {}
            if res.get('error',None)  :
                return Response( 
                        res,status=status.HTTP_200_OK
                    )
            return Response( 
                {"success": "reports Generation Starts. "},
                status=status.HTTP_200_OK
                )
        except ValidationError as e:
            return Response({"error":e.detail.get("error")}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":"server error"}, status=status.HTTP_200_OK)

class ReportSheetListAPIView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [SchoolPermissions.CAN_VIEW_RESULTS]
    
    def get(self, request,school_id,session_id,term_id,class_id) :
        try :
            cache_key = f"reportsheets_{session_id}_{term_id}_{class_id}"
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
                class_room__id = class_id
              ).prefetch_related('student').order_by('position')
            
            # we will include scores in the report for subjects 
            scores = StudentResult.objects.filter(
                batch__session__id = session_id,
                batch__term__id = term_id,
                batch__class_room__id = class_id
                )
            
            skills = StudentCharacterSkill.objects.filter(
                batch__session__id = session_id,
                batch__term__id = term_id,
                batch__class_room__id = class_id
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
class ReportSheetDetailAPIView(APIView):
    permission_classes=[HasSchoolPermission]
    permissions_required = [SchoolPermissions.CAN_VIEW_RESULTS]
    
    def get(self, request,school_id,session_id,term_id,class_id,student_id) :
        try :
            cache_key = f"reportsheet_{session_id}_{term_id}_{class_id}_{student_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # signal not cinfigured  
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
                        batch__class_room_id = class_id
                    ).select_related("batch")
                ),
                Prefetch(
                    "results",
                    queryset = StudentResult.objects.filter(
                        batch__session_id = session_id, 
                        batch__term_id = term_id,
                        batch__class_room_id = class_id
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
from rest_framework import permissions
class ReportSheetVerificationAPIView(APIView):
    permission_classes=[permissions.AllowAny]
    
    def get(self, request,school_tag,student_id,report_id,zero_or_one,adm) :
        try :
            if not any([school_tag,student_id,report_id,zero_or_one]) :
                    return Response({'error':'invalid request'}, status=status.HTTP_200_OK)
                
            report = ReportSheet.objects.filter(id=report_id,student_id =student_id).select_related('class_room','student__school','term','session').first()
            if not report :
                    return Response({'success':'not found','notVerified':True}, status=status.HTTP_200_OK)
            if not zero_or_one : #value is zero
                data = {
                    'first_name' : report.student.first_name,
                    'last_name' : report.student.last_name,
                    'middle_name' : report.student.middle_name,
                    'gender' : report.student.gender,
                    'cls' : report.class_room.name,
                }
                return Response({'success':'success','verificationRequired':True,'reportInfo':data}, status=status.HTTP_200_OK)
            
            if not adm.lower() == report.student.admission_number.lower() :
                return Response({'success':'invalid credencials','wrongeAdm':True,}, status=status.HTTP_200_OK)
            
            cache_key = f"reportsheet_{student_id}_{report_id}"
            try :
                cached_response = cache.get(cache_key)
                if cached_response :
                    # pass 
                    return Response(cached_response, status=status.HTTP_200_OK)
            except :
                pass
            student = Student.objects.filter(
                school__tag__exact = school_tag,
                id = student_id
            ).prefetch_related(
                Prefetch(
                    "skills",
                    queryset=StudentCharacterSkill.objects.filter(
                        batch__session_id = report.session_id,
                        batch__term_id = report.term_id,
                        batch__class_room_id = report.class_room_id
                    ).select_related("batch")
                ),
                Prefetch(
                    "results",
                    queryset = StudentResult.objects.filter(
                        batch__session_id = report.session_id, 
                        batch__term_id = report.term_id,
                        batch__class_room_id = report.class_room_id
                        ).select_related("batch"),
                ),
                Prefetch(
                    "report_sheets",
                    queryset=ReportSheet.objects.filter(
                        id=report_id
                    ),
                    to_attr="report_sheet",
                ),
            ).first()
            if not student :
                return Response({"error": "Invalid request!"}, status=status.HTTP_200_OK)
                
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
