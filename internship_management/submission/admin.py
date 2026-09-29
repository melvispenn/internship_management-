from django.contrib import admin

from .models import AssignmentSubmission, DailyReport, Feedback, Progress


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "intern",
        "assignment",
        "status",
        "submitted_at",
        "created_at",
    )
    list_filter = ("status", "submitted_at")
    search_fields = (
        "intern__name",
        "intern__user__email",
        "assignment__title",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = (
        "intern",
        "report_date",
        "status",
        "submission_date",
    )
    list_filter = ("status", "report_date")
    search_fields = (
        "intern__name",
        "intern__user__email",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "supervisor",
        "assignment_submission",
        "daily_report",
        "sticker",
        "created_at",
    )
    list_filter = ("sticker", "created_at")
    search_fields = (
        "supervisor__name",
        "comment",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "total_assignments",
        "validated_assignments",
        "percentage",
    )
    search_fields = (
        "enrollment__intern__name",
        "enrollment__intern__user__email",
    )
    readonly_fields = (
        "total_assignments",
        "validated_assignments",
        "percentage",
        "created_at",
        "updated_at",
    )