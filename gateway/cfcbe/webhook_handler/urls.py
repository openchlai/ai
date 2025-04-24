from django.urls import path

from webhook_handler import auth_views
from .views import CaseCategoryExportView, LocationExportView, TokenGenerationView, UnifiedWebhookView, WebformCategoriesView

urlpatterns = [
    path('webhook/<str:platform>/', UnifiedWebhookView.as_view(), name='unified-webhook'),
    # path('webhook/webform/categories/', WebformCategoriesView.as_view(), name='webform-categories'),
    # path('webhook/webform/locations-export/', LocationExportView.as_view(), name='locations-export'),
    # path('webhook/webform/auth/token/', TokenGenerationView.as_view(), name='token-generation'),
    # path('webhook/webform/case-categories-export/', CaseCategoryExportView.as_view(), name='case-categories-export'),
    path('webhook/webform/auth/request-verification/', auth_views.request_email_verification, name='request_email_verification'),
    path('webhook/webform/auth/verify-otp/', auth_views.verify_otp_and_issue_token, name='verify_otp'),
]
