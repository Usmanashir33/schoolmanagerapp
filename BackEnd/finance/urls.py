from django.urls import path
from .views import DirectorSchoolFeeSettingsView,DirectorFeeStartEngineView,DirectorFinanceDashbordView
from .views import StudentLedgerView,DirectorStudentPaymentView,DirectorPendingPaymentsView,DirectorSearchPaymentView
urlpatterns = [
    path('school-fee-settings/create/', DirectorSchoolFeeSettingsView.as_view(), name='create-school-fee-settings'),
    path('school-fee-settings/update/<str:fee_id>/', DirectorSchoolFeeSettingsView.as_view(), name='update-school-fee-settings'),
    path('school-fee-settings/delete/<str:school_id>/<str:fee_id>/<str:pin>/', DirectorSchoolFeeSettingsView.as_view(), name='delete-school-fee-settings'),
    path('school-fee-settings/set-fee-for-classes/', DirectorFeeStartEngineView.as_view(), name='set-fee-for-classes') ,
    path('school-fee-settings/set-fee-for-classes/<str:school_id>/<str:session>/<str:term>/', DirectorFeeStartEngineView.as_view(), name='get-fee-for-classes'),
    path('director-dashbord/<str:school_id>/<str:session>/<str:term>/<str:type>/', DirectorFinanceDashbordView.as_view(), name='director_dashbord'),
    path('director-payment-records/<str:school_id>/', DirectorPendingPaymentsView.as_view(), name='director_payment_records'),
    path('director-get-payment-records/<str:school_id>/<str:payment_id>/', DirectorStudentPaymentView.as_view(), name='director_get_payment_records'),
    path('trxs/student-ledger/<str:school_id>/<str:student_id>/', StudentLedgerView.as_view(), name='student_ledger'),
    
    path('director-payments/create/', DirectorStudentPaymentView.as_view(), name='payment'),
    path('search/payments/<str:school_id>/<str:ref_number>/', DirectorSearchPaymentView.as_view(), name='payment'),
]