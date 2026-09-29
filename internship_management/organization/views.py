import secrets
from datetime import timedelta
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from internship_management.users.models import Intern, Supervisor, User
from utils.email import EmailUtil

from .forms import InvitationAccountSetupForm, InvitationForm
from .models import Invitation


def _is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == "ADMIN")


def admin_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('users:login')}?next={request.path}")
        if not _is_admin(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped


def invitation_expiration(invitation):
    lifetime = timedelta(days=getattr(settings, "INVITATION_EXPIRY_DAYS", 7))
    return invitation.created_at + lifetime


def invitation_is_expired(invitation):
    return timezone.now() >= invitation_expiration(invitation)


def _decorate(invitation):
    invitation.expires_at = invitation_expiration(invitation)
    invitation.is_expired = invitation_is_expired(invitation)
    return invitation


def _invitation_context(invitation):
    return {
        "invitation": _decorate(invitation),
        "role_label": invitation.get_role_display(),
    }


@admin_required
def invitation_list(request):
    invitations = [_decorate(item) for item in Invitation.objects.select_related("invited_by")]
    return render(request, "invitation/invitation_list.html", {"invitations": invitations})


@admin_required
def invitation_create(request):
    form = InvitationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        invitation = form.save(commit=False)
        invitation.invited_by = request.user
        invitation.token = secrets.token_urlsafe(32)
        invitation.save()

        link = request.build_absolute_uri(
            reverse("organization:invitation_accept", kwargs={"token": invitation.token}),
        )
        sent = EmailUtil.send_invitation(
            email=invitation.email,
            name=invitation.email,
            role=invitation.get_role_display(),
            invitation_link=link,
            expiration=invitation_expiration(invitation),
        )
        if sent:
            messages.success(request, _("Invitation sent successfully."))
        else:
            messages.warning(
                request,
                _("The invitation was saved, but the email could not be sent."),
            )
        return redirect("organization:invitation_detail", invitation_id=invitation.pk)

    return render(request, "invitation/invite_user.html", {"form": form})


@admin_required
def invitation_detail(request, invitation_id):
    invitation = get_object_or_404(
        Invitation.objects.select_related("invited_by"),
        pk=invitation_id,
    )
    return render(request, "invitation/invitation_detail.html", _invitation_context(invitation))


@admin_required
def invitation_resend(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    if request.method != "POST":
        return redirect("organization:invitation_detail", invitation_id=invitation.pk)
    if invitation.status == "ACCEPTED":
        messages.error(request, _("An accepted invitation cannot be resent."))
        return redirect("organization:invitation_detail", invitation_id=invitation.pk)
    if invitation.status == "CANCELLED":
        messages.error(request, _("A revoked invitation cannot be resent."))
        return redirect("organization:invitation_detail", invitation_id=invitation.pk)

    invitation.token = secrets.token_urlsafe(32)
    invitation.status = "PENDING"
    invitation.created_at = timezone.now()
    invitation.save(update_fields=["token", "status", "created_at", "updated_at"])
    link = request.build_absolute_uri(
        reverse("organization:invitation_accept", kwargs={"token": invitation.token}),
    )
    sent = EmailUtil.send_invitation(
        email=invitation.email,
        name=invitation.email,
        role=invitation.get_role_display(),
        invitation_link=link,
        expiration=invitation_expiration(invitation),
    )
    messages.success(
        request,
        _("Invitation resent successfully.") if sent else _("Invitation updated, but the email could not be sent."),
    )
    return redirect("organization:invitation_detail", invitation_id=invitation.pk)


@admin_required
def invitation_revoke(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id)
    if request.method == "POST" and invitation.status == "PENDING":
        invitation.status = "CANCELLED"
        invitation.save(update_fields=["status", "updated_at"])
        messages.success(request, _("Invitation revoked."))
    return redirect("organization:invitation_detail", invitation_id=invitation.pk)


def _find_invitation(token):
    return Invitation.objects.select_related("invited_by").filter(token=token).first()


def invitation_accept(request, token):
    invitation = _find_invitation(token)
    if invitation is None:
        return render(request, "invitation/invitation_invalid.html", status=404)
    context = _invitation_context(invitation)
    if invitation.status == "CANCELLED":
        return render(request, "invitation/invitation_revoked.html", context, status=410)
    if invitation.status == "ACCEPTED":
        return render(request, "invitation/invitation_success.html", context)
    if invitation.status == "EXPIRED" or invitation_is_expired(invitation):
        return render(request, "invitation/invitation_expired.html", context, status=410)
    if request.method == "POST":
        return redirect("organization:invitation_setup", token=token)
    return render(request, "invitation/invitation_accept.html", context)


def invitation_setup(request, token):
    invitation = _find_invitation(token)
    if invitation is None:
        return render(request, "invitation/invitation_invalid.html", status=404)
    context = _invitation_context(invitation)
    if invitation.status == "CANCELLED":
        return render(request, "invitation/invitation_revoked.html", context, status=410)
    if invitation.status == "ACCEPTED":
        return render(request, "invitation/invitation_success.html", context)
    if invitation.status == "EXPIRED" or invitation_is_expired(invitation):
        return render(request, "invitation/invitation_expired.html", context, status=410)

    form = InvitationAccountSetupForm(
        request.POST or None,
        invitation=invitation,
    )
    if request.method == "POST" and form.is_valid():
        if User.objects.filter(email__iexact=invitation.email).exists():
            form.add_error(None, _("An account already exists for this email address."))
        else:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=invitation.email,
                    password=form.cleaned_data["password1"],
                    name=form.cleaned_data["name"],
                    role=invitation.role,
                    is_active=True,
                )
                if invitation.role == "INTERN":
                    Intern.objects.create(user=user, name=form.cleaned_data["name"])
                else:
                    Supervisor.objects.create(user=user, name=form.cleaned_data["name"])
                invitation.status = "ACCEPTED"
                invitation.accepted_at = timezone.now()
                invitation.save(update_fields=["status", "accepted_at", "updated_at"])
            login(request, user)
            return render(request, "invitation/invitation_success.html", {**context, "user": user})

    return render(request, "invitation/invitation_setup.html", {**context, "form": form})
