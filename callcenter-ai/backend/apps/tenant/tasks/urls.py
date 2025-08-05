
from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', views.TaskRetrieveUpdateDestroyView.as_view(), name='task-detail'),
    path('tags/', views.TaskTagListCreateView.as_view(), name='tasktag-list-create'),
    path('taggings/', views.TaskTaggingListCreateView.as_view(), name='tasktagging-list-create'),
    path('comments/', views.TaskCommentListCreateView.as_view(), name='taskcomment-list-create'),
    path('attachments/', views.TaskAttachmentListCreateView.as_view(), name='taskattachment-list-create'),
    path('reminders/', views.TaskReminderListCreateView.as_view(), name='taskreminder-list-create'),
    path('change-logs/', views.TaskChangeLogListView.as_view(), name='taskchangelog-list'),
]