from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login, logout
from django.db import connection

from .forms import LoginForm
from .forms import SignupForm

from internship_management.users.models import User
from django.shortcuts import render, redirect

from django.core.mail import send_mail
from django.contrib import messages
from .forms import OTPForm
from .models import Intern, OTP, User
from internship_management.attendance.models import Attendance
from internship_management.notifications.models import Notification
from internship_management.organization.models import Group
from internship_management.organization.models import InternEnrollment
from internship_management.organization.models import Invitation
from internship_management.organization.models import Speciality
from internship_management.organization.models import Supervision
from internship_management.submission.models import AssignmentSubmission
from internship_management.submission.models import DailyReport
from internship_management.submission.models import Progress
from internship_management.training.models import Assignment
from utils.enum import UserRole


if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()


def notifications_view(request):
    if not request.user.is_authenticated:
        return redirect("users:login")

    role = UserRole.ADMIN if request.user.is_superuser else (request.user.role or UserRole.INTERN)
    if role == "INTERN":
        notifications = Notification.objects.filter(intern__user=request.user)
    elif role == "SUPERVISOR":
        notifications = Notification.objects.filter(supervisor__user=request.user)
    else:
        notifications = Notification.objects.none()
    return render(request, "dashboard/notifications.html", {"notifications": notifications, "unread_notifications": notifications.filter(is_read=False).count(), "role": role})


def _dashboard_schema_ready():
    """Return whether the domain tables have the fields used by the dashboard."""
    required_tables = {
        "attendance_attendance": "is_deleted",
        "organization_group": "is_deleted",
        "submission_progress": "is_deleted",
        "training_assignment": "is_deleted",
        "notifications_notification": "is_deleted",
    }
    table_names = set(connection.introspection.table_names())
    if not required_tables.keys() <= table_names:
        return False

    with connection.cursor() as cursor:
        descriptions = {
            table: {
                column.name
                for column in connection.introspection.get_table_description(cursor, table)
            }
            for table in required_tables
        }
    return all(descriptions[table] >= {column} for table, column in required_tables.items())


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("users:login")

    # Superusers are administrators. Existing accounts created before the role
    # field was populated may have an empty value; give those accounts the
    # model's least-privileged default while still rejecting unknown roles.
    role = UserRole.ADMIN if request.user.is_superuser else (request.user.role or UserRole.INTERN)
    if role not in UserRole.values:
        raise PermissionDenied("Your account does not have a valid platform role.")

    context = {
        "user": request.user,
        "role": role,
        "notifications": [],
    }

    # Keep the existing dashboard available while the separately pending domain
    # migrations are repaired. The phone migration and authentication do not
    # depend on those tables, and rendering an empty role dashboard is safer
    # than allowing a missing domain column to turn login into a 500 response.
    dashboard_template = {
        "ADMIN": "dashboard/admin/page/index.html",
        "SUPERVISOR": "dashboard/supervisor/page/index.html",
        "INTERN": "dashboard/intern/page/index.html",
    }[role]

    if not _dashboard_schema_ready():
        return render(request, dashboard_template, context)

    if role == "ADMIN":
        total_attendance = Attendance.objects.count()
        present_attendance = Attendance.objects.filter(status="PRESENT").count()
        progress_values = [progress.percentage for progress in Progress.objects.select_related("enrollment__group")]
        context.update(
            {
                "stats": [
                    {"label": "Total interns", "value": User.objects.filter(role="INTERN").count(), "tone": "blue"},
                    {"label": "Supervisors", "value": User.objects.filter(role="SUPERVISOR").count(), "tone": "green"},
                    {"label": "Active groups", "value": Group.objects.filter(enrollments__is_active=True).distinct().count(), "tone": "navy"},
                    {"label": "Departments", "value": Speciality.objects.count(), "tone": "bright"},
                ],
                "attendance_rate": round((present_attendance / total_attendance) * 100) if total_attendance else 0,
                "progress_rate": round(sum(progress_values) / len(progress_values)) if progress_values else 0,
                "pending_invitations": Invitation.objects.filter(status="PENDING").count(),
                "pending_reviews": AssignmentSubmission.objects.filter(status="SUBMITTED").count(),
                "recent_users": User.objects.order_by("-date_joined")[:5],
                "unread_notifications": 0,
            },
        )
    elif role == "SUPERVISOR":
        supervisor = getattr(request.user, "supervisor_profile", None)
        supervisions = Supervision.objects.filter(supervisor=supervisor, is_active=True) if supervisor else Supervision.objects.none()
        enrollments = InternEnrollment.objects.filter(group__supervisions__in=supervisions, is_active=True).select_related("intern__user", "group")
        intern_ids = enrollments.values_list("intern_id", flat=True)
        total_attendance = Attendance.objects.filter(enrollment__in=enrollments).count()
        present_attendance = Attendance.objects.filter(enrollment__in=enrollments, status="PRESENT").count()
        context.update(
            {
                "stats": [
                    {"label": "Assigned interns", "value": enrollments.values("intern_id").distinct().count(), "tone": "blue"},
                    {"label": "Attendance rate", "value": f"{round((present_attendance / total_attendance) * 100) if total_attendance else 0}%", "tone": "green"},
                    {"label": "Pending submissions", "value": AssignmentSubmission.objects.filter(intern_id__in=intern_ids, status="SUBMITTED").count(), "tone": "bright"},
                    {"label": "Reports to review", "value": DailyReport.objects.filter(intern_id__in=intern_ids, status="SUBMITTED").count(), "tone": "navy"},
                ],
                "assigned_interns": enrollments[:8],
                "active_groups": supervisions.select_related("group__speciality"),
                "pending_reviews": AssignmentSubmission.objects.filter(intern_id__in=intern_ids, status="SUBMITTED").select_related("intern", "assignment").order_by("-submitted_at")[:5],
                "unread_notifications": Notification.objects.filter(supervisor=supervisor, is_read=False).count() if supervisor else 0,
            },
        )
    else:
        intern = getattr(request.user, "intern_profile", None)
        enrollments = InternEnrollment.objects.filter(intern=intern, is_active=True).select_related("group__speciality") if intern else InternEnrollment.objects.none()
        assignments = Assignment.objects.filter(module__training_program__group__enrollments__in=enrollments, status="PUBLISHED").distinct()
        submissions = AssignmentSubmission.objects.filter(intern=intern) if intern else AssignmentSubmission.objects.none()
        total_assignments = assignments.count()
        validated_assignments = submissions.filter(status="VALIDATED").count()
        attendance = Attendance.objects.filter(enrollment__in=enrollments)
        present = attendance.filter(status="PRESENT").count()
        context.update(
            {
                "stats": [
                    {"label": _("Overall progress"), "value": f"{round((validated_assignments / total_assignments) * 100) if total_assignments else 0}%", "tone": "blue", "icon": "progress"},
                    {"label": _("Attendance"), "value": f"{round((present / attendance.count()) * 100) if attendance.count() else 0}%", "tone": "green", "icon": "attendance"},
                    {"label": _("Pending assignments"), "value": submissions.exclude(status="VALIDATED").count(), "tone": "bright", "icon": "assignments"},
                    {"label": _("Submitted"), "value": submissions.filter(status__in=["SUBMITTED", "VALIDATED"]).count(), "tone": "navy", "icon": "report"},
                ],
                "enrollments": enrollments,
                "recent_reports": DailyReport.objects.filter(intern=intern).order_by("-report_date")[:5] if intern else DailyReport.objects.none(),
                "recent_submissions": submissions.select_related("assignment").order_by("-updated_at")[:5],
                "unread_notifications": Notification.objects.filter(intern=intern, is_read=False).count() if intern else 0,
            },
        )
    return render(
        request,
        dashboard_template,
        context,
    )

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Intern.objects.create(user=user, name=user.name)

            code = OTP.generate_code()

            OTP.objects.create(
                user=user,
                code=code,
            )

            email_sent = send_mail(
                subject="Your Internship Management OTP",
                message=f"Your OTP code is: {code}\n\nThis code is valid for 5 minutes.",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=True,
            )

            if email_sent:
                messages.info(request, "A verification code was sent to your email address.")
            else:
                messages.warning(
                    request,
                    "Your account was created, but the verification email could not be sent. "
                    "Please contact an administrator or retry after email is configured.",
                )

            request.session["otp_user_id"] = user.id

            return redirect("users:otp")

    else:
        form = SignupForm()

    return render(
        request,
        "users/signup.html",
        {"form": form},
    )

def otp(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        return redirect("users:signup")

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        form = OTPForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]

            otp_code = OTP.objects.filter(
                user=user,
                code=code,
                is_used=False,
            ).order_by("-created_at").first()

            if otp_code and otp_code.is_valid():
                otp_code.is_used = True
                otp_code.save()

                user.is_active = True
                user.save()

                del request.session["otp_user_id"]

                login(request, user)
                messages.success(request, "Your email has been verified. Welcome to InPACE!")
                return redirect(settings.LOGIN_REDIRECT_URL)

            form.add_error(
                "code",
                "Invalid or expired OTP code.",
            )

    else:
        form = OTPForm()

    return render(
        request,
        "users/otp.html",
        {"form": form},
    )

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password"]
            account = User.objects.filter(email__iexact=email).first()

            # Give users a useful explanation when signup created the account
            # but email/OTP verification has not been completed yet.
            if account and not account.is_active and account.check_password(password):
                form.add_error(
                    None,
                    "Your account is not active yet. Please complete email verification before signing in.",
                )
                return render(request, "users/login.html", {"form": form})

            user = authenticate(
                request,
                email=account.email if account else email,
                password=password,
            )
            if user is not None:
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)

            form.add_error(None, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(
        request,
        "users/login.html",
        {"form": form},
    )
def logout_view(request):
    logout(request)
    return redirect("users:login")
