from django.urls import path
from .views import *

urlpatterns = [
    path('', ApiRootView.as_view(), name='api-root'),  # Root view for /api/
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    path('home/', HomeView.as_view(), name='home'),  # Landing page route,
    path('proof-of-identity/', ProofOfIdentityView.as_view(), name='proof-of-identity'),
    path('proof-of-address/', ProofOfAddressView.as_view(), name='proof-of-address'),
]
