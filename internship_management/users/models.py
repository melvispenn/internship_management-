
from typing import ClassVar
import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.db.models import CharField
from django.db.models import EmailField
from django.db.models import BooleanField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import CASCADE
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel
from utils.enum import UserRole
from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Internship Management.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    role = CharField(
        _("role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.INTERN,
    )
    email = EmailField(_("email address"), unique=True)

    phone = models.CharField( _("phone number"), max_length=30, blank=True, )

   

    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class OTP(models.Model):
    """One-time email verification code for a newly registered user."""

    code = CharField(_("code"), max_length=6)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_used = BooleanField(_("used"), default=False)
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="otps",
        verbose_name=_("user"),
    )

    @staticmethod
    def generate_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    def is_valid(self) -> bool:
        return not self.is_used and timezone.now() <= self.created_at + timedelta(minutes=5)


class Supervisor(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="supervisor_profile",
        verbose_name=_("user account"),
    )
    name = CharField(_("name"), max_length=150)
    phone_number = PhoneNumberField(_("phone number"), blank=True)

    class Meta:
        verbose_name = _("supervisor")
        verbose_name_plural = _("supervisors")

    def __str__(self) -> str:
        return self.name


class Intern(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="intern_profile",
        verbose_name=_("user account"),
    )
    name = CharField(_("name"), max_length=150)
    phone_number = PhoneNumberField(_("phone number"), blank=True)
    date_joined = models.DateField(_("date joined"), null=True, blank=True)
    start_date = models.DateField(_("start date"), null=True, blank=True)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    leaving_date = models.DateField(_("leaving date"), null=True, blank=True)

    class Meta:
        verbose_name = _("intern")
        verbose_name_plural = _("interns")

    def __str__(self) -> str:
        return self.name
