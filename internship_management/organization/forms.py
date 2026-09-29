from datetime import timedelta

from django import forms
from django.contrib.auth import password_validation
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Invitation


class InvitationForm(forms.ModelForm):
    """Form used by administrators to invite an intern or supervisor."""

    class Meta:
        model = Invitation
        fields = ("email", "role")
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "auth-input",
                    "autocomplete": "email",
                    "placeholder": _("recipient@example.com"),
                },
            ),
            "role": forms.Select(attrs={"class": "auth-input"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        cutoff = timezone.now() - timedelta(
            days=getattr(settings, "INVITATION_EXPIRY_DAYS", 7),
        )
        if Invitation.objects.filter(
            email__iexact=email,
            status="PENDING",
            created_at__gte=cutoff,
        ).exists():
            raise forms.ValidationError(
                _("A pending invitation already exists for this email address."),
            )
        return email


class InvitationAccountSetupForm(forms.Form):
    """Account credentials for a recipient; the invitation supplies the role."""

    name = forms.CharField(
        label=_("Full name"),
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "auth-input", "autocomplete": "name"},
        ),
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "auth-input", "autocomplete": "new-password"},
        ),
    )
    password2 = forms.CharField(
        label=_("Confirm password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "auth-input", "autocomplete": "new-password"},
        ),
    )

    def __init__(self, *args, invitation=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.invitation = invitation

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        password_validation.validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError(_("The passwords do not match."))
        return cleaned_data
