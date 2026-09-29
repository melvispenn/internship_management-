"""
Custom model managers for the Internship Management System.

Provides:
- SoftDeleteManager: returns only active records by default.
- AllObjectsManager: returns all records, including soft-deleted records.
"""

from __future__ import annotations

from django.db import models


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted records."""

    def get_queryset(self):
        """Return only records that have not been soft-deleted."""
        return super().get_queryset().filter(is_deleted=False)


class AllObjectsManager(models.Manager):
    """Manager that returns all records, including soft-deleted records."""

    def get_queryset(self):
        """Return the complete queryset without filtering deleted records."""
        return super().get_queryset()