from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from utils.enum import (
    AssignmentStatus,
    DocumentStatus,
    ModuleStatus,
    TrainingProgramStatus,
)
from utils.slug import SlugFunctions


class TrainingProgram(BaseModel):
    group = models.OneToOneField(
        "organization.Group",
        on_delete=models.PROTECT,
        related_name="training_program",
        verbose_name=_("group"),
    )

    name = models.CharField(
        _("name"),
        max_length=200,
    )

    description = models.TextField(
        _("description"),
        blank=True,
    )

    start_date = models.DateField(
        _("start date"),
    )

    end_date = models.DateField(
        _("end date"),
    )

    issue_date = models.DateTimeField(
        _("issue date"),
        null=True,
        blank=True,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=TrainingProgramStatus.choices,
        default=TrainingProgramStatus.DRAFT,
    )

    created_by = models.ForeignKey(
        "users.Supervisor",
        on_delete=models.PROTECT,
        related_name="created_training_programs",
        verbose_name=_("created by"),
    )

    slug = models.SlugField(
        _("slug"),
        max_length=150,
        unique=True,
    )

    class Meta:
        verbose_name = _("training program")
        verbose_name_plural = _("training programs")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = SlugFunctions.generate_unique_slug(self, self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Module(BaseModel):
    training_program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name=_("training program"),
    )

    name = models.CharField(
        _("name"),
        max_length=200,
    )

    description = models.TextField(
        _("description"),
        blank=True,
    )

    order = models.PositiveIntegerField(
        _("order"),
        default=0,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=ModuleStatus.choices,
        default=ModuleStatus.DRAFT,
    )

   

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Document(BaseModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("module"),
    )

    title = models.CharField(
        _("title"),
        max_length=200,
    )

    content = models.TextField(
        _("content"),
        blank=True,
    )

    file = models.FileField(
        _("file"),
        upload_to="training/documents/",
        blank=True,
        null=True,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.DRAFT,
    )

    

    class Meta:
        verbose_name = _("document")
        verbose_name_plural = _("documents")

    def __str__(self):
        return self.title


class Assignment(BaseModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name=_("module"),
    )

    title = models.CharField(
        _("title"),
        max_length=200,
    )

    instructions = models.TextField(
        _("instructions"),
    )

    content = models.TextField(
        _("content"),
        blank=True,
    )

    file = models.FileField(
        _("file"),
        upload_to="training/assignments/",
        blank=True,
        null=True,
    )

    due_date = models.DateTimeField(
        _("due date"),
        null=True,
        blank=True,
    )

    status = models.CharField(
        _("status"),
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.DRAFT,
    )

    slug = models.SlugField(
        _("slug"),
        max_length=150,
        unique=True,
    )

   
    class Meta:
        verbose_name = _("assignment")
        verbose_name_plural = _("assignments")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = SlugFunctions.generate_unique_slug(self, self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
