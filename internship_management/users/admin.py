from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import Intern, OTP, Supervisor, User


if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    if "allauth.account" in settings.INSTALLED_APPS:
        from allauth.account.decorators import secure_admin_login

        # Force the `admin` sign in process to go through the `django-allauth` workflow:
        # https://docs.allauth.org/en/latest/common/admin.html#admin
        admin.autodiscover()
        admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]
    else:
        # Keep the optional setting safe when allauth is intentionally disabled.
        def admin_login_fallback(request):
            return redirect(f"{reverse(settings.LOGIN_URL)}?next={request.path}")

        admin.site.login = admin_login_fallback  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (_("Account role"), {"fields": ("role",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "name", "role", "is_superuser"]
    list_filter = ["role", "is_active", "is_staff"]
    search_fields = ["name"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )





class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal information",
            {
                "fields": (
                    "name",
                    "role",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    list_display = (
        "email",
        "name",
        "role",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "email",
        "name",
    )

    ordering = ("email",)

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "is_used",
        "created_at",
    )

    list_filter = (
        "is_used",
        "created_at",
    )

    search_fields = (
        "user__email",
        "code",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "phone_number",
        "created_at",
    )

    search_fields = (
        "name",
        "user__email",
        "phone_number",
    )

    list_filter = ("created_at",)


@admin.register(Intern)
class InternAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "user",
        "phone_number",
        "start_date",
        "end_date",
        "leaving_date",
    )

    search_fields = (
        "name",
        "user__email",
        "phone_number",
    )

    list_filter = (
        "start_date",
        "end_date",
        "leaving_date",
    )
