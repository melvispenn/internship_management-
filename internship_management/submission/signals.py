from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from internship_management.notifications.services import (
    create_notification,
)
from utils.enum import (
    DailyReportStatus,
    NotificationType,
    SubmissionStatus,
)

from .models import AssignmentSubmission, DailyReport, Feedback


@receiver(post_save, sender=AssignmentSubmission)
def notify_supervisor_on_submission(
    sender,
    instance,
    created,
    **kwargs,
):
    if not created:
        return

    supervisor = (
        instance.assignment.module.training_program.created_by
    )

    create_notification(
        notification_type=NotificationType.SUBMISSION_RECEIVED,
        supervisor=supervisor,
    )


@receiver(post_save, sender=DailyReport)
def notify_supervisor_on_daily_report(
    sender,
    instance,
    created,
    **kwargs,
):
    if not created:
        return

    if instance.status != DailyReportStatus.SUBMITTED:
        return

    enrollment = (
        instance.intern.enrollments
        .filter(is_active=True)
        .select_related(
            "group__training_program__created_by"
        )
        .first()
    )

    if not enrollment:
        return

    supervisor = enrollment.group.training_program.created_by

    create_notification(
        notification_type=NotificationType.DAILY_REPORT,
        supervisor=supervisor,
    )


@receiver(post_save, sender=Feedback)
def notify_intern_on_feedback(
    sender,
    instance,
    created,
    **kwargs,
):
    if not created:
        return

    if instance.assignment_submission:
        intern = instance.assignment_submission.intern

    elif instance.daily_report:
        intern = instance.daily_report.intern

    else:
        return

    create_notification(
        notification_type=NotificationType.FEEDBACK_RECEIVED,
        intern=intern,
    )


@receiver(pre_save, sender=AssignmentSubmission)
def track_submission_status_change(
    sender,
    instance,
    **kwargs,
):
    if not instance.pk:
        instance._previous_status = None
        return

    previous = (
        sender.objects
        .filter(pk=instance.pk)
        .values("status")
        .first()
    )

    instance._previous_status = (
        previous["status"] if previous else None
    )


@receiver(post_save, sender=AssignmentSubmission)
def notify_intern_on_submission_status_change(
    sender,
    instance,
    created,
    **kwargs,
):
    if created:
        return

    previous_status = getattr(
        instance,
        "_previous_status",
        None,
    )

    if previous_status == instance.status:
        return

    if instance.status == SubmissionStatus.VALIDATED:
        create_notification(
            notification_type=NotificationType.SUBMISSION_VALIDATED,
            intern=instance.intern,
        )

    elif instance.status == SubmissionStatus.REJECTED:
        create_notification(
            notification_type=NotificationType.SUBMISSION_REJECTED,
            intern=instance.intern,
        )