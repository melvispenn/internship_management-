from .models import Notification


NOTIFICATION_MESSAGES = {
    "SUBMISSION_RECEIVED": "New submission",
    "DAILY_REPORT": "New daily report",
    "SUBMISSION_VALIDATED": "Submission validated",
    "SUBMISSION_REJECTED": "Submission rejected",
    "FEEDBACK_RECEIVED": "New feedback",
    "MODULE_SENT": "New module",
    "DOCUMENT_SENT": "New document",
    "ASSIGNMENT_SENT": "New assignment",
}


def create_notification(
    *,
    notification_type,
    intern=None,
    supervisor=None,
):
    title = NOTIFICATION_MESSAGES.get(
        notification_type,
        "New notification",
    )

    return Notification.objects.create(
        intern=intern,
        supervisor=supervisor,
        notification_type=notification_type,
        title=title,
        message=title,
    )