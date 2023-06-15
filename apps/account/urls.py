from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path("register/", views.RegisterAPIView.as_view(), name='register'),
    path("login/", TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("activate/<uuid:activation_code>/", views.ActivationApiView.as_view(), name='activation_code'),
    path("change_password/", views.ChangePasswordAPIView.as_view(), name='change_password'),
    path("forgot_password/", views.ForgotPasswordAPIView.as_view(), name='change_password'),
    path("forgot_password_complete/", views.ForgotPasswordCompleteAPIView.as_view(), name='change_password'),
    path("delete/account/", views.DeleteAccountAPIView.as_view(), name='delete_account'),
]