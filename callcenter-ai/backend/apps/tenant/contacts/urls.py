from django.urls import path
from . import views

urlpatterns = [
    # Contact Types
    path('types/', views.ContactTypeListCreateView.as_view(), name='contact-type-list'),
    path('types/<int:pk>/', views.ContactTypeRetrieveUpdateDestroyView.as_view(), name='contact-type-detail'),
    
    # Contact Tags
    path('tags/', views.ContactTagListCreateView.as_view(), name='contact-tag-list'),
    path('tags/<int:pk>/', views.ContactTagRetrieveUpdateDestroyView.as_view(), name='contact-tag-detail'),
    
    # Contact Groups
    path('groups/', views.ContactGroupListCreateView.as_view(), name='contact-group-list'),
    path('groups/<int:pk>/', views.ContactGroupRetrieveUpdateDestroyView.as_view(), name='contact-group-detail'),
    
    # Contacts
    path('', views.ContactListCreateView.as_view(), name='contact-list'),
    path('<int:pk>/', views.ContactRetrieveUpdateDestroyView.as_view(), name='contact-detail'),
    
    # Contact Interactions
    path('<int:contact_pk>/interactions/', views.ContactInteractionListCreateView.as_view(), name='contact-interaction-list'),
    path('<int:contact_pk>/interactions/<int:pk>/', views.ContactInteractionRetrieveUpdateDestroyView.as_view(), name='contact-interaction-detail'),
    
    # Contact Type Assignments
    path('<int:contact_pk>/types/', views.ContactContactTypeListCreateView.as_view(), name='contact-type-assignment-list'),
    
    # Contact Tag Assignments
    path('<int:contact_pk>/tags/', views.ContactTagAssignmentListCreateView.as_view(), name='contact-tag-assignment-list'),
]