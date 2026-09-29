from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from utils.enum import NotificationType


class Notification(BaseModel):
    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("intern"),
        null=True,
        blank=True,
    )

    supervisor = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("supervisor"),
        null=True,
        blank=True,
    )

    notification_type = models.CharField(
        _("notification type"),
        max_length=30,
        choices=NotificationType.choices,
    )

    title = models.CharField(
        _("title"),
        max_length=200,
    )

    message = models.TextField(
        _("message"),
    )

    is_read = models.BooleanField(
        _("read"),
        default=False,
    )

    read_at = models.DateTimeField( _("read at"), null=True, blank=True, )

    

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(intern__isnull=False)
                    | Q(supervisor__isnull=False)
                )
                & ~(
                    Q(intern__isnull=False)
                    & Q(supervisor__isnull=False)
                ),
                name="notification_has_one_recipient",
            ),
        ]

    def __str__(self):
        return self.title
