from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from utils.enum import AttendanceStatus


class Attendance(BaseModel):
    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name=_("intern"),
        null=True,
        blank=True,
    )

    enrollment = models.ForeignKey(
        "organization.InternEnrollment",
        on_delete=models.PROTECT,
        related_name="attendance_records",
        verbose_name=_("intern enrollment"),
    )

    marked_by = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.PROTECT,
        related_name="attendance_marked",
        verbose_name=_("marked by"),
    )

    date = models.DateField(
        _("date"),
    )

    status = models.CharField(
        _("status"),
        max_length=10,
        choices=AttendanceStatus.choices,
    )

    check_in = models.DateTimeField(
        _("check in"),
        null=True,
        blank=True,
    )

    check_out = models.DateTimeField(
        _("check out"),
        null=True,
        blank=True,
    )

    verification_code = models.CharField(
        _("verification code"),
        max_length=20,
        blank=True,
    )

    class Meta:
        verbose_name = _("attendance")
        verbose_name_plural = _("attendance records")
        ordering = ["-date"]

        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "date"],
                name="unique_enrollment_attendance_per_day",
            ),
        ]

    def __str__(self):
        return f"{self.enrollment.intern} - {self.date}"

