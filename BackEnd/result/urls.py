

from django.urls import path
from . views import DirecterResultBatchUpsertView, FetchResultBatchView ,DownloadScoreTemplateView, UploadScoresAPIView ,GenerateReportSheetAPIView
from . views import DirectorBatchLockAPIView ,FetchReportSheetAPIView  ,DownloadSkillTemplateView,StudentsSkillsUpsertOrGetView,UploadSkillAPIView
from . views import DirectorBatchApproveAPIView,ApprovalHistoriesView
urlpatterns = [
    path("result-batch/upsert/", DirecterResultBatchUpsertView.as_view()),
    path("result-batch/fetch/<str:school_id>/<str:session_id>/<str:term_id>/", FetchResultBatchView.as_view()),
    
    path("result-batch/download/<str:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/<str:subject_id>/", DownloadScoreTemplateView.as_view()),
    path("result-batch/upload/", UploadScoresAPIView.as_view()),
    
    path("result-skill/download/<str:school_id>/<str:session_id>/<str:term_id>/<str:class_id>/", DownloadSkillTemplateView.as_view()),
    path("result-skill/save/", StudentsSkillsUpsertOrGetView.as_view()),
    path("result-skill/fetch/<str:school_id>/<str:session_id>/<str:term_id>/", StudentsSkillsUpsertOrGetView.as_view()),
    path("result-skill/upload/", UploadSkillAPIView.as_view()),
    
    path("result-editing/approval/", DirectorBatchApproveAPIView.as_view()),
    path("result-editing/locking/", DirectorBatchLockAPIView.as_view()),
    path("approval-history/fetch/<str:school_id>/", ApprovalHistoriesView.as_view()),
    path("result-batch/generate-report-sheets/"  , GenerateReportSheetAPIView.as_view()),
    path("reportsheet/fetch/<str:student_id>/<str:term_id>/<str:class_id>/", FetchReportSheetAPIView.as_view()),
]


   