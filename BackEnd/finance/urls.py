from django.urls import path
from .views import * 
urlpatterns = [
    path('dashbord/<uuid:school_id>/<str:session>/<str:term>/<str:type>/', FinanceDashbordView.as_view(), name='director_dashbord'), # Done enhencement
    path('all-student-trx/<uuid:school_id>/<str:session>/<str:term>/<str:type>/', FinanceDashbordAllStudentsTrxView.as_view(), name='director_dashbord'), # Done enhencement
    path('school-fee-settings/set-fee-for-classes/', FeeStartEngineView.as_view(), name='set-fee-for-classes') , #Done
    path('school-fee-settings/set-fee-for-classes/<str:school_id>/<str:session>/<str:term>/', FeeStartEngineView.as_view(), name='get-fee-for-classes'), # done 
    
    path('school-fee-settings/create/', SchoolFeeSettingsView.as_view(), name='create-school-fee-settings'), #Done
    path('school-fee-settings/update/<str:fee_id>/', SchoolFeeSettingsView.as_view(), name='update-school-fee-settings'), #Done
    path('school-fee-settings/delete/<str:school_id>/<str:fee_id>/<str:pin>/', SchoolFeeSettingsView.as_view(), name='delete-school-fee-settings'), #Done
    
    path('get-payment-records/<str:school_id>/<str:payment_id>/', StudentPaymentView.as_view(), name='get_payment_records'), #Done
    path('payments/create/', StudentPaymentOnlyStaffView.as_view(), name='payments'), #Done
    path('payment-records/<str:school_id>/', PendingPaymentsView.as_view(), name='payment_records'), #Done
    path('trxs/student-ledger/<str:school_id>/<str:student_id>/', StudentLedgerView.as_view(), name='student_ledger'),#Done
    
    path('search/payments/<str:school_id>/<str:ref_number>/', SearchPaymentView.as_view(), name='payment'),# Done
    
]