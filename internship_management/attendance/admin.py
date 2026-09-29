from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "marked_by",
        "date",
        "status",
        "check_in",
        "check_out",
    )

    list_filter = (
        "status",
        "date",
        "marked_by",
    )

    search_fields = (
        "enrollment__intern__name",
        "enrollment__intern__user__email",
        "marked_by__name",
    )

    ordering = ("-date",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )