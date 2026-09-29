from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from utils.enum import (
    DailyReportStatus,
    FeedbackSticker,
    SubmissionStatus,
)


class AssignmentSubmission(BaseModel):
    assignment = models.ForeignKey(
        "training.Assignment",
        on_delete=models.PROTECT,
        related_name="submissions",
        verbose_name=_("assignment"),
    )

    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.PROTECT,
        related_name="assignment_submissions",
        verbose_name=_("intern"),
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.TO_DO,
    )

    file = models.FileField(
        _("file"),
        upload_to="submissions/assignments/",
        blank=True,
        null=True,
    )

    link = models.URLField(
        _("link"),
        blank=True,
    )

    submitted_at = models.DateTimeField(
        _("submitted at"),
        null=True,
        blank=True,
    )

    validated_at = models.DateTimeField(
        _("validated at"),
        null=True,
        blank=True,
    )

    validated_by = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.SET_NULL,
        related_name="validated_submissions",
        verbose_name=_("validated by"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("assignment submission")
        verbose_name_plural = _("assignment submissions")

        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "intern"],
                name="unique_assignment_submission_per_intern",
            ),
        ]

    def __str__(self):
        return f"{self.intern} - {self.assignment}"


class DailyReport(BaseModel):
    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.PROTECT,
        related_name="daily_reports",
        verbose_name=_("intern"),
    )

    report_date = models.DateField(
        _("report date"),
    )

    previous_work_done = models.TextField(
        _("previous work done"),
        null=True,
        blank=True,
    )

    today_plan = models.TextField(
        _("today's plan"),
    )

    challenges = models.TextField(
        _("challenges"),
        blank=True,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=DailyReportStatus.choices,
        default=DailyReportStatus.DRAFT,
    )

    submission_date = models.DateTimeField(
        _("submission date"),
        null=True,
        blank=True,
    )

    reviewed_by = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.SET_NULL,
        related_name="reviewed_daily_reports",
        verbose_name=_("reviewed by"),
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(
        _("reviewed at"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("daily report")
        verbose_name_plural = _("daily reports")
        ordering = ["-report_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["intern", "report_date"],
                name="unique_daily_report_per_intern",
            ),
        ]

    def __str__(self):
        return f"{self.intern} - {self.report_date}"


class Feedback(BaseModel):
    supervisor = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.PROTECT,
        related_name="feedback_given",
        verbose_name=_("supervisor"),
    )

    assignment_submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name="feedback",
        verbose_name=_("assignment submission"),
        null=True,
        blank=True,
    )

    daily_report = models.ForeignKey(
        DailyReport,
        on_delete=models.CASCADE,
        related_name="feedback",
        verbose_name=_("daily report"),
        null=True,
        blank=True,
    )

    comment = models.TextField(
        _("comment"),
        blank=True,
    )

    sticker = models.CharField(
        _("sticker"),
        max_length=30,
        choices=FeedbackSticker.choices,
        blank=True,
    )

    class Meta:
        verbose_name = _("feedback")
        verbose_name_plural = _("feedback")

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(assignment_submission__isnull=False)
                    | Q(daily_report__isnull=False)
                )
                & ~(
                    Q(assignment_submission__isnull=False)
                    & Q(daily_report__isnull=False)
                ),
                name="feedback_has_one_target",
            ),
        ]

    def __str__(self):
        return f"Feedback - {self.supervisor}"


class Progress(BaseModel):

    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.PROTECT,
        related_name="progress_records",
        verbose_name=_("intern"),
        null=True,
        blank=True,
    )
         
    
    enrollment = models.OneToOneField(
        "organization.InternEnrollment",
        on_delete=models.CASCADE,
        related_name="progress",
        verbose_name=_("intern enrollment"),
    )
    completed_assignments = models.PositiveIntegerField( 
        _("completed assignments"), default=0, 
        ) 

    last_updated = models.DateTimeField(
          _("last updated"),
            auto_now=True, 
            )
    
    class Meta:
        verbose_name = _("progress")
        verbose_name_plural = _("progress")

    def _get_assignments(self):
        from internship_management.training.models import Assignment

        return Assignment.objects.filter(
            module__training_program__group=self.enrollment.group,
        )

    @property
    def total_assignments(self):
        return self._get_assignments().count()

    @property
    def validated_assignments(self):
        return AssignmentSubmission.objects.filter(
            intern=self.enrollment.intern,
            assignment__module__training_program__group=self.enrollment.group,
            status=SubmissionStatus.VALIDATED,
        ).count()

    @property
    def percentage(self):
        total = self.total_assignments

        if total == 0:
            return 0

        return round(
            (self.validated_assignments / total) * 100,
            2,
        )

    def __str__(self):
        return f"Progress - {self.enrollment.intern}"
