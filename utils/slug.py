
"""
Slug utility helpers for the Internship Management System.

This module provides reusable utilities for:
- Secure random suffix generation.
- Globally unique slug generation.
- Relationship-scoped unique slug generation.
- Automatic handling of Django slug field max_length.
- Collision handling for models using slugs.

Typical sluggable models in this project include:
- Speciality
- Group
- TrainingProgram
- Module
- Document
- Assignment

Usage
-----
    # In a model's save() method:

    self.slug = SlugFunctions.unique_slug_generator_by_name(self)

    # Or when the slug is based on another field:

    self.slug = SlugFunctions.generate_unique_slug(
        self,
        self.title,
    )

    # For a slug that must only be unique within a related object:

    self.slug = SlugFunctions.generate_unique_slug_for_related_object(
        self,
        self.title,
        related_field_name="training_program",
    )
"""

from __future__ import annotations

import logging
import secrets
import string
from typing import Any

from django.utils.text import slugify


logger = logging.getLogger(__name__)


class SlugFunctions:
    """Reusable slug-generation utilities for the project.

    The class acts as a namespace for slug-related helper functions.
    It is not intended to be instantiated.
    """

    # Number of random characters used to resolve slug collisions.
    RANDOM_SUFFIX_LENGTH: int = 6

    # Characters allowed in generated random suffixes.
    RANDOM_CHARS: str = string.ascii_lowercase + string.digits

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_slug_max_length(instance: Any) -> int:
        """Return the max_length configured on the model's slug field.

        Raises
        ------
        AttributeError
            If the model does not define a ``slug`` field.
        """
        klass = instance.__class__

        try:
            return klass._meta.get_field("slug").max_length
        except Exception as exc:
            logger.exception(
                "Unable to retrieve slug field metadata for %s.",
                klass.__name__,
            )

            message = (
                f"Model {klass.__name__!r} must define a 'slug' field."
            )

            raise AttributeError(message) from exc

    # -------------------------------------------------------------------------
    # Random string generation
    # -------------------------------------------------------------------------

    @staticmethod
    def random_string_generator(
        size: int = RANDOM_SUFFIX_LENGTH,
        chars: str = RANDOM_CHARS,
    ) -> str:
        """Generate a cryptographically secure random string.

        ``secrets.choice`` is used instead of ``random.choice`` because the
        generated value may become part of a publicly visible URL.
        """
        return "".join(
            secrets.choice(chars)
            for _ in range(size)
        )

    # -------------------------------------------------------------------------
    # Global unique slug
    # -------------------------------------------------------------------------

    @staticmethod
    def generate_unique_slug(
        instance: Any,
        field_value: str,
        max_attempts: int = 100,
    ) -> str:
        """Generate a globally unique slug for a model instance.

        The value is first converted using Django's ``slugify`` function.
        If the generated slug already exists, a random suffix is appended
        until a unique value is found.

        Existing instances are excluded from the uniqueness check so that
        updating an object does not generate a new slug unnecessarily.

        Parameters
        ----------
        instance:
            Model instance receiving the slug.

        field_value:
            Value from which the slug will be generated.

        max_attempts:
            Maximum number of collision-resolution attempts.

        Raises
        ------
        AttributeError
            If the model does not contain a slug field.

        ValueError
            If a unique slug cannot be generated.
        """
        klass = instance.__class__
        max_length = SlugFunctions._get_slug_max_length(instance)

        base_slug = slugify(field_value)

        # Make sure the initial slug respects the model's max_length.
        base_slug = base_slug[:max_length]

        candidate = base_slug

        for attempt in range(max_attempts):
            queryset = klass.objects.filter(slug=candidate)

            # When updating an existing object, ignore itself.
            if instance.pk:
                queryset = queryset.exclude(pk=instance.pk)

            if not queryset.exists():
                logger.debug(
                    "Unique slug generated for %s after %d attempt(s): %s",
                    klass.__name__,
                    attempt + 1,
                    candidate,
                )
                return candidate

            # A collision occurred, therefore generate a new suffix.
            suffix = SlugFunctions.random_string_generator()

            # Reserve space for "-" and the random suffix.
            trim_to = (
                max_length
                - SlugFunctions.RANDOM_SUFFIX_LENGTH
                - 1
            )

            candidate = f"{base_slug[:trim_to]}-{suffix}"

        message = (
            f"Unable to generate a unique slug for "
            f"{klass.__name__!r} after {max_attempts} attempts."
        )

        logger.error(message)

        raise ValueError(message)

    # -------------------------------------------------------------------------
    # Relationship-scoped unique slug
    # -------------------------------------------------------------------------

    @staticmethod
    def generate_unique_slug_for_related_object(
        instance: Any,
        field_value: str,
        related_field_name: str,
        max_attempts: int = 100,
    ) -> str:
        """Generate a slug unique within a related object.

        This is useful when uniqueness depends on a parent relationship.

        Example
        -------
        Two different TrainingPrograms may contain a Module named
        ``Introduction``. Therefore, the module slug only needs to be unique
        within its own TrainingProgram.

        Example usage::

            self.slug = SlugFunctions.generate_unique_slug_for_related_object(
                self,
                self.title,
                related_field_name="training_program",
            )

        Parameters
        ----------
        instance:
            Model instance receiving the slug.

        field_value:
            Value from which the slug is generated.

        related_field_name:
            ForeignKey field defining the uniqueness scope.

        max_attempts:
            Maximum number of collision-resolution attempts.

        Raises
        ------
        AttributeError
            If the model does not contain the specified relationship.

        ValueError
            If a unique slug cannot be generated.
        """
        klass = instance.__class__
        max_length = SlugFunctions._get_slug_max_length(instance)

        try:
            related_instance = getattr(
                instance,
                related_field_name,
            )
        except AttributeError as exc:
            message = (
                f"Model {klass.__name__!r} must have a related field "
                f"{related_field_name!r}."
            )

            logger.exception(message)

            raise AttributeError(message) from exc

        base_slug = slugify(field_value)[:max_length]
        candidate = base_slug

        for attempt in range(max_attempts):
            filter_kwargs: dict[str, Any] = {
                "slug": candidate,
                related_field_name: related_instance,
            }

            queryset = klass.objects.filter(**filter_kwargs)

            # Exclude the current object when updating.
            if instance.pk:
                queryset = queryset.exclude(pk=instance.pk)

            if not queryset.exists():
                logger.debug(
                    "Unique scoped slug generated for %s after %d attempt(s): %s",
                    klass.__name__,
                    attempt + 1,
                    candidate,
                )
                return candidate

            suffix = SlugFunctions.random_string_generator()

            trim_to = (
                max_length
                - SlugFunctions.RANDOM_SUFFIX_LENGTH
                - 1
            )

            candidate = f"{base_slug[:trim_to]}-{suffix}"

        message = (
            f"Unable to generate a unique slug for {klass.__name__!r} "
            f"within {related_field_name!r} after "
            f"{max_attempts} attempts."
        )

        logger.error(message)

        raise ValueError(message)

    # -------------------------------------------------------------------------
    # Convenience helper
    # -------------------------------------------------------------------------

    @staticmethod
    def unique_slug_generator_by_name(instance: Any) -> str:
        """Generate a unique slug from an instance's ``name`` field.

        This is a convenience method for models such as:
        - Speciality
        - Group

        Raises
        ------
        AttributeError
            If the instance does not contain a ``name`` field.
        """
        if not hasattr(instance, "name"):
            message = (
                f"Model {instance.__class__.__name__!r} "
                "must have a 'name' attribute."
            )

            raise AttributeError(message)

        return SlugFunctions.generate_unique_slug(
            instance,
            instance.name,
        )

