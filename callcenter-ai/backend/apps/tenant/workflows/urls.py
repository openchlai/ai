from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Workflow Templates URLs
# router.register(r'workflow-templates', views.WorkflowTemplateViewSet, basename='workflowtemplate')

urlpatterns = [
    path('', include(router.urls)),
    
    # Content Types
    path('content-types/', views.ContentTypeListView.as_view(), name='content-type-list'),
    
    # Workflow Templates
    path('workflows/', views.WorkflowTemplateListCreateView.as_view(), name='workflow-list-create'),
    path('workflows/<uuid:pk>/', views.WorkflowTemplateRetrieveUpdateDestroyView.as_view(), name='workflow-detail'),
    
    # Stages (nested under workflows)
    path('workflows/<uuid:workflow_id>/stages/', views.StageListCreateView.as_view(), name='stage-list-create'),
    path('workflows/<uuid:workflow_id>/stages/<uuid:pk>/', views.StageRetrieveUpdateDestroyView.as_view(), name='stage-detail'),
    
    # Transitions (nested under workflows)
    path('workflows/<uuid:workflow_id>/transitions/', views.TransitionListCreateView.as_view(), name='transition-list-create'),
    path('workflows/<uuid:workflow_id>/transitions/<uuid:pk>/', views.TransitionRetrieveUpdateDestroyView.as_view(), name='transition-detail'),
    
    # Workflow Instances
    path('instances/', views.WorkflowInstanceListCreateView.as_view(), name='workflow-instance-list-create'),
    path('instances/<uuid:pk>/', views.WorkflowInstanceRetrieveUpdateDestroyView.as_view(), name='workflow-instance-detail'),
    
    # Stage Instances (nested under workflow instances)
    path('instances/<uuid:workflow_instance_id>/stage-instances/', views.StageInstanceListCreateView.as_view(), name='stage-instance-list-create'),
    path('instances/<uuid:workflow_instance_id>/stage-instances/<uuid:pk>/', views.StageInstanceRetrieveUpdateDestroyView.as_view(), name='stage-instance-detail'),
    
    # Transition Logs (nested under workflow instances)
    path('instances/<uuid:workflow_instance_id>/transition-logs/', views.TransitionLogListView.as_view(), name='transition-log-list'),
    
    # SLAs (nested under stages)
    path('stages/<uuid:stage_id>/slas/', views.SLAListCreateView.as_view(), name='sla-list-create'),
    path('stages/<uuid:stage_id>/slas/<uuid:pk>/', views.SLARetrieveUpdateDestroyView.as_view(), name='sla-detail'),
    
    # Escalations (nested under stage instances)
    path('stage-instances/<uuid:stage_instance_id>/escalations/', views.EscalationListCreateView.as_view(), name='escalation-list-create'),
    path('stage-instances/<uuid:stage_instance_id>/escalations/<uuid:pk>/', views.EscalationRetrieveUpdateDestroyView.as_view(), name='escalation-detail'),
]