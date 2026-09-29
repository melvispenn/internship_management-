from django.db.models.signals import post_save
from django.dispatch import receiver

from internship_management.notifications.services import create_notification
from utils.enum import NotificationType

from .models import Assignment, Document, Module


@receiver(post_save, sender=Module)
def notify_interns_on_module_published(
    sender,
    instance,
    created,
    **kwargs,
):
    if instance.status != "PUBLISHED":
        return

    interns = instance.training_program.group.enrollments.filter(
        is_active=True
    ).select_related("intern")

    for enrollment in interns:
        create_notification(
            notification_type=NotificationType.MODULE_SENT,
            intern=enrollment.intern,
        )


@receiver(post_save, sender=Document)
def notify_interns_on_document_published(
    sender,
    instance,
    created,
    **kwargs,
):
    if instance.status != "PUBLISHED":
        return

    interns = instance.module.training_program.group.enrollments.filter(
        is_active=True
    ).select_related("intern")

    for enrollment in interns:
        create_notification(
            notification_type=NotificationType.DOCUMENT_SENT,
            intern=enrollment.intern,
        )


@receiver(post_save, sender=Assignment)
def notify_interns_on_assignment_published(
    sender,
    instance,
    created,
    **kwargs,
):
    if instance.status != "PUBLISHED":
        return

    interns = instance.module.training_program.group.enrollments.filter(
        is_active=True
    ).select_related("intern")

    for enrollment in interns:
        create_notification(
            notification_type=NotificationType.ASSIGNMENT_SENT,
            intern=enrollment.intern,
        )