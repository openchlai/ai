from django.urls import path, include
from apps.shared.tenants.views import create_tenant
from apps.shared.accounts.urls import urlpatterns as accounts_urlpatterns

urlpatterns = [
    path("api/v1/tenants/", create_tenant, name="create-tenant"),
    path("api/v1/accounts/", include(accounts_urlpatterns)),
]
