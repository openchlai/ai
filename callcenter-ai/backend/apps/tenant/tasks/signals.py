from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.db import transaction

@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    if instance.pk:
        original = Task.objects.get(pk=instance.pk)
        changed_fields = []
        
        for field in ['status', 'priority', 'assigned_to', 'due_date']:
            original_value = getattr(original, field)
            new_value = getattr(instance, field)
            if original_value != new_value:
                changed_fields.append(field)
                
        if changed_fields:
            # This will be processed in post_save to ensure instance is saved first
            instance._changed_fields = changed_fields


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    if created:
        # Log task creation
        TaskChangeLog.objects.create(
            task=instance,
            changed_by=instance.created_by,
            field='created',
            new_value='Task created'
        )
        
        # Create notification for assignee if assigned
        if instance.assigned_to:
            Notification.objects.create(
                recipient=instance.assigned_to,
                title=f"New Task Assigned: {instance.title}",
                message=instance.description[:200],
                related_object=instance,
                notification_type='task_assigned'
            )
    else:
        # Log changes if any
        if hasattr(instance, '_changed_fields'):
            original = Task.objects.get(pk=instance.pk)
            changed_by = getattr(instance, '_changed_by', None)
            
            for field in instance._changed_fields:
                old_value = getattr(original, field)
                new_value = getattr(instance, field)
                
                if isinstance(old_value, models.Model):
                    old_value = str(old_value)
                if isinstance(new_value, models.Model):
                    new_value = str(new_value)
                
                TaskChangeLog.objects.create(
                    task=instance,
                    changed_by=changed_by or instance.assigned_to or instance.created_by,
                    field=field,
                    old_value=old_value,
                    new_value=new_value
                )
                
                # Special handling for status changes
                if field == 'status':
                    if new_value == Task.Status.COMPLETED:
                        Notification.objects.create(
                            recipient=instance.created_by,
                            title=f"Task Completed: {instance.title}",
                            message=f"The task '{instance.title}' has been marked as completed",
                            related_object=instance,
                            notification_type='task_completed'
                        )
                    elif new_value == Task.Status.IN_PROGRESS:
                        Notification.objects.create(
                            recipient=instance.created_by,
                            title=f"Task Started: {instance.title}",
                            message=f"The task '{instance.title}' is now in progress",
                            related_object=instance,
                            notification_type='task_started'
                        )
            
            del instance._changed_fields


@receiver(m2m_changed, sender=Task.tags.through)
def task_tags_changed(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        changed_by = getattr(instance, '_changed_by', None)
        
        if action == 'post_add':
            field = 'tags_added'
            new_tags = list(TaskTag.objects.filter(pk__in=pk_set).values_list('name', flat=True))
            TaskChangeLog.objects.create(
                task=instance,
                changed_by=changed_by or instance.assigned_to or instance.created_by,
                field=field,
                new_value=', '.join(new_tags)
            )
        elif action == 'post_remove':
            field = 'tags_removed'
            removed_tags = list(TaskTag.objects.filter(pk__in=pk_set).values_list('name', flat=True))
            TaskChangeLog.objects.create(
                task=instance,
                changed_by=changed_by or instance.assigned_to or instance.created_by,
                field=field,
                old_value=', '.join(removed_tags)
            )