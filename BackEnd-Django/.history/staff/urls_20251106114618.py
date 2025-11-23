from .views import StaffUsersDashboardView,StaffUserDetailView,WithdrawalRequestView,StaffTrxsDashboardView,StaffTrxDetailView
from .views import AnalysisRequestView
from django.urls import path

urlpatterns = [
    path('users/', StaffUsersDashboardView.as_view(),name='all-users'),
    path('trxs/', StaffTrxsDashboardView.as_view(),name='all-trxs'),
    path('user/<uuid:user_id>/',StaffUserDetailView.as_view(),name='user-staff'),
    path('trx/<uuid:trx_id>/',StaffTrxDetailView.as_view(),name='trx-staff'),
    path('withdrawal-requests/',WithdrawalRequestView.as_view(),name='withdrawal-requests'),
    path('analysis/',AnalysisRequestView.as_view(),name='analysis'),
    path('paymen/',AnalysisRequestView.as_view(),name='analysis'),

]