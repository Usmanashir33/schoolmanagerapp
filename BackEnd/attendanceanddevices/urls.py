from django.urls import path

from .views import (
    FaceDetectionView,
    BiometricIdentityView,
    DeviceView,
)

urlpatterns = [

    path(
        "face-detection/",
        FaceDetectionView.as_view()
    ),

    path(
        "fetch_ident/<str:school_id>/",
        BiometricIdentityView.as_view()
    ),
    path(
        "create_ident/<str:school_id>/",
        BiometricIdentityView.as_view()
    ),

    path(
        "delete_ident/<str:school_id>/<str:biometric_id>/<str:pin>/",
        BiometricIdentityView.as_view()
    ),

    path(
        "update_ident/<str:school_id>/<str:biometric_id>/",
        BiometricIdentityView.as_view()
    ),
    

    path(
        "fetch_device/<str:school_id>/",
        DeviceView.as_view()
    ),
    path(
        "create_device/<str:school_id>/",
        DeviceView.as_view()
    ),

    path(
        "delete_device/<str:school_id>/<str:device_id>/<str:pin>/",
        DeviceView.as_view()
    ),

    path(
        "update_device/<str:school_id>/<str:device_id>/",
        DeviceView.as_view()
    ),
]