from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from utils.enum import (
    InvitationRole,
    InvitationStatus,
)

class Speciality(BaseModel):
    name = models.CharField(
        _("name"),
        max_length=150,
        unique=True,
    )

    description = models.TextField(
        _("description"),
        blank=True,
    )

    slug = models.SlugField(
        _("slug"),
        max_length=150,
        unique=True,
    )
    is_active = models.BooleanField(
        _("description"), 
        blank=True,
        default=True,
    )


    class Meta:
        verbose_name = _("speciality")
        verbose_name_plural = _("specialities")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Group(BaseModel):
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.PROTECT,
        related_name="groups",
        verbose_name=_("speciality"),
    )

    name = models.CharField(
        _("name"),
        max_length=150,
    )

    date_creation = models.DateField(
        _("date of creation"),
        auto_now_add=True,
    )

    description = models.TextField(
            _("description"),
            blank=True,
        )

    is_active = models.BooleanField(
            _("description"), 
            blank=True,
            default=True,
        )
    

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["speciality", "name"],
                name="unique_group_per_speciality",
            ),
        ]

    def __str__(self):
        return f"{self.speciality.name} - {self.name}"


class Invitation(BaseModel):
    email = models.EmailField(
        _("email"),
    )

    role = models.CharField(
        _("role"),
        max_length=20,
        choices=InvitationRole.choices,
    )

    invited_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="sent_invitations",
        verbose_name=_("invited by"),
        limit_choices_to={"role": "ADMIN"},
    )

    token = models.CharField(
        _("token"),
        max_length=255,
        unique=True,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
    )

    accepted_at = models.DateTimeField(
        _("accepted at"),
        null=True,
        blank=True,
    )

    expired_at =  models.DateTimeField(
        _("expired at"),
        null=True,
        blank=True,
    )


    class Meta:
        verbose_name = _("invitation")
        verbose_name_plural = _("invitations")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.role}"


class InternEnrollment(BaseModel):
    intern = models.ForeignKey(
        "users.Intern",
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name=_("intern"),
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="enrollments",
        verbose_name=_("group"),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    Status = models.CharField(
        _("status"),
        max_length=20,
        default="ACTIVE",
    )

    class Meta:
        verbose_name = _("intern enrollment")
        verbose_name_plural = _("intern enrollments")

        constraints = [
            models.UniqueConstraint(
                fields=["intern", "group"],
                name="unique_intern_group_enrollment",
            ),
        ]

    def __str__(self):
        return f"{self.intern} - {self.group}"


class Supervision(BaseModel):
    supervisor = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.PROTECT,
        related_name="supervisions",
        verbose_name=_("supervisor"),
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="supervisions",
        verbose_name=_("group"),
    )

    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    is_active = models.BooleanField(
        _("is active"),
        default=True,
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    class Meta:
        verbose_name = _("supervision")
        verbose_name_plural = _("supervisions")

        constraints = [
            models.UniqueConstraint(
                fields=["supervisor", "group"],
                name="unique_supervisor_group",
            ),
        ]

    def __str__(self):
        return f"{self.supervisor} - {self.group}"
