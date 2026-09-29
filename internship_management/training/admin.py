from django.contrib import admin

from .models import Assignment, Document, Module, TrainingProgram


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "group",
        "created_by",
        "start_date",
        "end_date",
        "status",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "name",
        "group__name",
        "created_by__name",
    )

    ordering = ("-created_at",)


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "training_program",
        "order",
        "status",
    )

    list_filter = (
        "status",
        "training_program",
    )

    search_fields = (
        "name",
        "training_program__name",
    )

    ordering = (
        "training_program",
        "order",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "module",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "module",
    )

    search_fields = (
        "title",
        "module__name",
    )

    ordering = ("-created_at",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "module",
        "status",
        "due_date",
        "created_at",
    )

    list_filter = (
        "status",
        "due_date",
        "module",
    )

    search_fields = (
        "title",
        "module__name",
    )

    ordering = ("-created_at",)