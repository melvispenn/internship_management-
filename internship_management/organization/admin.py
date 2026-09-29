from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import (
    Group,
    InternEnrollment,
    Invitation,
    Speciality,
    Supervision,
)


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = ("name",)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "speciality",
        "date_creation",
    )

    list_filter = (
        "speciality",
    )

    search_fields = (
        "name",
        "speciality__name",
    )

    ordering = (
        "speciality",
        "name",
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "role",
        "status",
        "invited_by",
        "accepted_at",
        "created_at",
    )

    list_filter = (
        "role",
        "status",
    )

    search_fields = (
        "email",
        "invited_by__email",
    )

    readonly_fields = (
        "token",
        "accepted_at",
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)


@admin.register(InternEnrollment)
class InternEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "intern",
        "group",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "group",
    )

    search_fields = (
        "intern__name",
        "intern__user__email",
        "group__name",
    )

    ordering = ("-created_at",)


@admin.register(Supervision)
class SupervisionAdmin(admin.ModelAdmin):
    list_display = (
        "supervisor",
        "group",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "group",
    )

    search_fields = (
        "supervisor__name",
        "supervisor__user__email",
        "group__name",
    )

    ordering = ("-created_at",)
