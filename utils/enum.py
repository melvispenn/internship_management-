from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    SUPERVISOR = "SUPERVISOR", _("Supervisor")
    INTERN = "INTERN", _("Intern")


class InvitationRole(models.TextChoices):
    INTERN = "INTERN", _("Intern")
    SUPERVISOR = "SUPERVISOR", _("Supervisor")


class InvitationStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    ACCEPTED = "ACCEPTED", _("Accepted")
    EXPIRED = "EXPIRED", _("Expired")
    CANCELLED = "CANCELLED", _("Cancelled")


class TrainingProgramStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    ACTIVE = "ACTIVE", _("Active")
    COMPLETED = "COMPLETED", _("Completed")


class ModuleStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")


class DocumentStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")


class AssignmentStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PUBLISHED = "PUBLISHED", _("Published")
    CLOSED = "CLOSED", _("Closed")


class SubmissionStatus(models.TextChoices):
    TO_DO = "TO_DO", _("To do")
    ONGOING = "ONGOING", _("Ongoing")
    SUBMITTED = "SUBMITTED", _("Submitted")
    VALIDATED = "VALIDATED", _("Validated")
    REJECTED = "REJECTED", _("Rejected")
    SUBMISSION_RECEIVED = "SUBMISSION_RECEIVED", _("Submission received")


class AttendanceStatus(models.TextChoices):
    PRESENT = "PRESENT", _("Present")
    ABSENT = "ABSENT", _("Absent")


class DailyReportStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    SUBMITTED = "SUBMITTED", _("Submitted")
    REVIEWED = "REVIEWED", _("Reviewed")


class FeedbackSticker(models.TextChoices):
    GOOD = "GOOD", _("Good")
    VERY_GOOD = "VERY_GOOD", _("Very good")
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT", _("Needs improvement")
    EXCELLENT = "EXCELLENT", _("Excellent")


class NotificationType(models.TextChoices):
    MODULE_SENT = "MODULE_SENT", _("Module sent")
    DOCUMENT_SENT = "DOCUMENT_SENT", _("Document sent")
    ASSIGNMENT_SENT = "ASSIGNMENT_SENT", _("Assignment sent")
    SUBMISSION_VALIDATED = "SUBMISSION_VALIDATED", _("Submission validated")
    SUBMISSION_REJECTED = "SUBMISSION_REJECTED", _("Submission rejected")
    FEEDBACK_RECEIVED = "FEEDBACK_RECEIVED", _("Feedback received")
    DAILY_REPORT = "DAILY_REPORT", _("Daily report")
