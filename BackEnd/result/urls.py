from django.urls import path
from . views import *
from . teacher_views import *

urlpatterns = [
    path("result-batch/fetch/<str:school_id>/<str:session_id>/<str:term_id>/", FetchResultBatchView.as_view()), # Done 
    path("result-batch/detail/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/<str:subject_id>/", FetchResultBatchDetailView.as_view()), # Done 
    path("result-batch/upsert/", ResultBatchUpsertView.as_view()),  #Done
    path("result-batch/download/<str:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/<str:subject_id>/", DownloadScoreTemplateView.as_view()), #Done
    path("result-batch/upload/", UploadScoresAPIView.as_view()), #Done
    path("approval-history/fetch/<str:school_id>/", ApprovalHistoriesView.as_view()), #Done
    
    path("result-editing/managing/", BatchManageAPIView.as_view()),#Done
    path("result-editing/approval/", BatchApproveAPIView.as_view()), #Done
    
    path("result-skill/save/", StudentsSkillsUpsertOrGetView.as_view()), #Done
    path("result-skill/fetch/<str:school_id>/<str:session_id>/<str:term_id>/", StudentsSkillsUpsertOrGetView.as_view()), # Done
    path("result-skill/detail/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/", FetchSkillBatchDetailView.as_view()), # Done 
    
    path("result-skill/download/<str:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/", DownloadSkillTemplateView.as_view()), #Done
    path("result-skill/upload/", UploadSkillAPIView.as_view()), #Done
    path("generate-report-sheets/"  , GenerateClassReportSheetAPIView.as_view()), #Done
    path("fetchreportsheets/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/", ReportSheetListAPIView.as_view()), #Done
    path("reportrecords/<uuid:school_id>/<str:session_id>/<str:term_id>/", ReportRecordListAPIView.as_view()), #Done
    path("fetchreportsheet/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/<str:student_id>/", ReportSheetDetailAPIView.as_view()), #Done
    path("fetchstudentreportsheet/<uuid:school_id>/<str:term_id>/<str:class_id>/<str:student_id>/", StudentReportSheetDetailAPIView.as_view()), #Done
    path("verification/<str:school_tag>/<str:student_id>/<str:report_id>/<int:zero_or_one>/<path:adm>/", ReportSheetVerificationAPIView.as_view()), #Done
    
    #------------------------------------------Teacher Site End points----------------------------------------
    path("result-batch/fetch-by-teacher/<str:school_id>/<str:session_id>/<str:term_id>/", TeacherFetchResultBatchView.as_view()), # Done 
    path("result-skill/fetch-by-teacher/<str:school_id>/<str:session_id>/<str:term_id>/", TeacherStudentsSkillsUpsertOrGetView.as_view()), # Done
   
    path("reportrecords-by-teacher/<uuid:school_id>/<str:session_id>/<str:term_id>/", TeacherReportRecordListAPIView.as_view()), #Done
    path("result-editing/managing-by-teacher/", TeacherBatchManageAPIView.as_view()),#Done
    
    path("fetchreportsheets-by-teacher/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/", TeacherReportSheetListAPIView.as_view()), #Done
    path("fetchreportsheet-by-teacher/<uuid:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/<str:student_id>/", TeacherReportSheetDetailAPIView.as_view()), #Done
    
    path("result-batch/upsert-by-teacher/", TeacherResultBatchUpsertView.as_view()),  #Done
    path("result-skill/save-by-teacher/", TeacherStudentsSkillsUpsertOrGetView.as_view()), #Done
    
    path("result-batch/upload-by-teacher/", TeacherUploadScoresAPIView.as_view()), #Done
    path("result-skill/upload-by-teacher/", TeacherUploadSkillAPIView.as_view()), #Done
    
]


   