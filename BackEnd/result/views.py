from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.exceptions import ValidationError


from academics.models import Subject,ClassRoom

from .utils import build_student_records_workbook , decript_scores_from_workbook,generate_report_and_position
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

from .serializers import ResultBatchReadSerializer, ResultBatchReadSerializer, ResultBatchUpsertSerializer
from .serializers import ReportSheetFetchSerializer,StudentCharAndSkillsUpsertSerializer,SkillBatchReadSerializer
from . serializers import ApprovalRecordSerializer
class DirecterResultBatchUpsertView(APIView):
    permission_classes = [DirectorUserPermission]
    
    def post(self, request):
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

            serializer = ResultBatchUpsertSerializer(data=request.data)

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
    permission_classes = [DirectorUserPermission]
    
    def get(self, request,school_id, session_id, term_id):
        try :
            director = request.user.director
            # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            batches = ResultBatch.objects.filter(
                class_room__section__school__id = school_id,
                session_id=session_id,
                term_id=term_id
            )
            serializer = ResultBatchReadSerializer(batches, many=True).data 

            return Response( 
                    {"success": "Results fetched successfully.", "filteredBatches": serializer},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)

class ApprovalHistoriesView(APIView):
    def get(self, request,school_id) :
        try :
            director = request.user.director
            # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            history = ApprovalRecord.objects.filter(school__id = school_id).order_by("-timestamp")[:100]
            serializer = ApprovalRecordSerializer(history, many=True).data 
            return Response( 
                    {"success": "history fetched successfully.", "approvalHistories": serializer},
                    status=status.HTTP_200_OK )
        except Exception as e :
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)

class DownloadScoreTemplateView(APIView):
    permission_classes = [DirectorUserPermission]
    def get(self, request, school_id, session_id, term_id ,class_id,subject_id):
        
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
            "subject_id"  : subject_id,
        }
        workbook_stream = build_student_records_workbook(
            request_data,
            students,
            school_name = valid_school.first().name,
            class_name = ClassRoom.objects.filter(id=class_id,section__school__id=school_id).first().name,
            term_name=valid_school.first().terms.filter(id=term_id).first().name,
            session_name=valid_school.first().sessions.filter(id=session_id).first().name,
            subject_name=valid_school.first().subjects.filter(id=subject_id).first().name
        )

        response = HttpResponse(
            workbook_stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = (
            'attachment; filename="score_template.xlsx"'
        )

        return response

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

class DirectorBatchLockAPIView(APIView):
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            batch_id = request.data.get("batch")
            target = request.data.get("target") # Options CHAR | RESULT
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            batch = ResultBatch.objects.filter(
                    id = batch_id
                ).first() if target == "RESULT" else  CharacterBatch.objects.filter(
                    id = batch_id
                ).first() if target == "CHAR" else None
           
            if not batch :
                return Response({"error": "Invalid Batch"}, status=status.HTTP_200_OK)
                
            #  lock or unlock 
            batch.is_locked = not batch.is_locked
            batch.save()
            if not batch.is_locked :
                batch.approved = False 
                batch.save()
            
            sta = "Locked" if batch.is_locked else "Unlocked"
            uiFieldName = "currentBatch" if  target == "RESULT" else "currentSkills" if target == "CHAR" else None 
            
            data = ResultBatchReadSerializer(batch).data if  target == "RESULT" else SkillBatchReadSerializer(batch).data if target == "CHAR" else None 
            
            return Response( 
                    {"success": f"Results {sta} successfully.", uiFieldName: data},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)

class DirectorBatchApproveAPIView(APIView):
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            batch_ids = request.data.get("batchIds")
            target = request.data.get("target") # Options CHAR | RESULT
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
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
                batch.save()
                if batch .approved :
                    batch.is_locked = True
                    batch.save()
            # generate record here 
            
            descriptions = [
                str(b.class_room.name) for b in batches
            ] if target == "CHAR" else [
                str(f"{b.class_room.name}_{b.subject.name}") for b in batches
            ] if target == "RESULT" else ["Not Recognized"]
            
            history = ApprovalRecord.objects.create(
                school = valid_school.first(),
                description	 = f"Approved: {",".join(descriptions)}|{target}",
                directorName = director.full_name() ,	 
                batchCount = batches.count() ,	 
            )
            history_data = ApprovalRecordSerializer(history).data 
            
            sta = "Approved" if batch.is_locked else "Rejected"
            uiFieldName = "approvedResults" if  target == "RESULT" else "approvedSkills" if target == "CHAR" else None 
            
            data = ResultBatchReadSerializer(batches,many=True).data if  target == "RESULT" else SkillBatchReadSerializer(batches,many=True).data if target == "CHAR" else None 
            
            return Response( 
                    {"success": f"Results {sta} successfully.", uiFieldName: data,"history":history_data},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        
class UploadScoresAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            file = request.FILES.get("file")
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_200_OK)
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            students = Student.objects.filter(
                class_rooms__class_room__id=class_id,
                class_rooms__status__in=["active", "enrolled"],
            ).distinct().order_by("-joined_at")
            
            result_data, error = decript_scores_from_workbook(file,request,students)
            if error :
                return Response({"error": error }, status=status.HTTP_200_OK)
            
            serializer = ResultBatchUpsertSerializer(data=result_data)
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
        
class StudentsSkillsUpsertOrGetView(APIView):
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            serializer = StudentCharAndSkillsUpsertSerializer (data=request.data)
            if serializer.is_valid():
                batch = serializer.save()
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
            director = request.user.director
            # validate director actions 
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            batches = CharacterBatch.objects.filter(
                class_room__section__school__id = school_id,
                session_id=session_id,
                term_id=term_id
            )
            serializer = SkillBatchReadSerializer(batches, many=True).data 
            return Response( 
                    {"success": "Skills fetched successfully.", "filteredCharAndSkills": serializer},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response({"error": 'server error'}, status=status.HTTP_200_OK)
        

class UploadSkillAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            file = request.FILES.get("file")
            if not file:
                return Response({"error": "No file uploaded"}, status=status.HTTP_200_OK)
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            students = Student.objects.filter(
                class_rooms__class_room__id=class_id,
                class_rooms__status__in=["active", "enrolled"],
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

class GenerateReportSheetAPIView(APIView):
    permission_classes = [DirectorUserPermission]

    def post(self, request):
        try :
            director = request.user.director
            # validate director actions 
            pin = request.data.get("pin")
            school_id = request.data.get("school")
            class_id = request.data.get("class_room")
            term_id = request.data.get("term")
            session_id = request.data.get("session")
            
            if not request.user.pins.checkPin(pin) :
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_200_OK)
            valid_school = School.objects.filter(director_id = director.id, id=school_id)  #.exists()
            if not valid_school:
                return Response({"error": "Invalid Director Entry"}, status=status.HTTP_200_OK)
            
            students = Student.objects.filter(
                class_rooms__class_room__id=class_id,
                class_rooms__status__in=["active", "enrolled"],
            ).distinct().order_by("-joined_at") 
            
            report_data = generate_report_and_position(term_id,session_id,class_id,students)
            print('report_data: ', report_data)
            return Response( 
                    {"success": "reports Generated "} ,
                    status=status.HTTP_200_OK
                )
        except ValidationError as e:
            return Response({"error":e.detail.get("error")}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":"server error"}, status=status.HTTP_200_OK)

class FetchReportSheetAPIView(APIView):
    # permission_classes = [DirectorUserPermission]
    def get(self, request, student_id,term_id,class_id) :
        # try :
            report = ReportSheet.objects.filter(
                student__id = student_id, 
                term__id = term_id,
                class_room__id = class_id
              ).first()
            
            # we will include scores in the report for subjects 
            scores = StudentResult.objects.filter(
                student__id = student_id, 
                batch__term__id = term_id,
                batch__class_room__id = class_id
                )
            
            if not report or not scores :
                return Response({"success": "Report not found"}, status=status.HTTP_200_OK)
            
            serializer = ReportSheetFetchSerializer(report,context={"scores":scores})
            return Response( 
                    {"success": "Report Fetched ","studentReport" :  serializer.data} ,
                    status=status.HTTP_200_OK
                )
        # except Exception as e:
            # return Response({"error": 'server error'}, status=status.HTTP_200_OK)