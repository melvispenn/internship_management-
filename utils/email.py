from __future__ import annotations

from typing import Any

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import translation


class EmailUtil:
    """Email utilities for the Internship Management System."""

    @staticmethod
    def send(
        subject: str,
        recipients: list[str],
        template: str,
        context: dict[str, Any] | None = None,
        language: str | None = None,
    ) -> bool:
        """Send a templated HTML email."""

        if not recipients:
            return False

        current_language = translation.get_language()
        context = context or {}

        try:
            if language:
                translation.activate(language)

            context.update({
                "site_name": getattr(
                    settings,
                    "SITE_NAME",
                    "Internship Management",
                ),
                "site_url": getattr(
                    settings,
                    "BASE_URL",
                    "",
                ),
            })

            body = render_to_string(
                template_name=template,
                context=context,
            )

            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=getattr(
                    settings,
                    "DEFAULT_FROM_EMAIL",
                    "noreply@example.com",
                ),
                to=recipients,
            )

            email.content_subtype = "html"
            email.send()

            return True

        except Exception:
            return False

        finally:
            translation.activate(current_language)

    @staticmethod
    def send_otp(
        email: str,
        otp: str,
        language: str | None = None,
    ) -> bool:
        return EmailUtil.send(
            subject="Your verification code",
            recipients=[email],
            template="emails/otp.html",
            context={"otp": otp},
            language=language,
        )

    @staticmethod
    def send_invitation(
        email: str,
        name: str,
        role: str,
        invitation_link: str,
        expiration: Any | None = None,
        language: str | None = None,
    ) -> bool:
        context = {
            "name": name,
            "role": role,
            "invitation_link": invitation_link,
            "expiration": expiration,
        }
        subject = render_to_string(
            "invitation/invitation_email_subject.txt",
            context,
        ).strip()
        return EmailUtil.send(
            subject=subject or "Internship Management Invitation",
            recipients=[email],
            template="invitation/invitation_email.html",
            context=context,
            language=language,
        )

    @staticmethod
    def send_daily_report_notification(
        email: str,
        intern_name: str,
        report_date: str,
        language: str | None = None,
    ) -> bool:
        return EmailUtil.send(
            subject="Daily Report Submitted",
            recipients=[email],
            template="emails/daily_report.html",
            context={
                "intern_name": intern_name,
                "report_date": report_date,
            },
            language=language,
        )

    @staticmethod
    def send_report_feedback(
        email: str,
        report_date: str,
        feedback: str,
        language: str | None = None,
    ) -> bool:
        return EmailUtil.send(
            subject="Feedback on Your Daily Report",
            recipients=[email],
            template="emails/report_feedback.html",
            context={
                "report_date": report_date,
                "feedback": feedback,
            },
            language=language,
        )

    @staticmethod
    def send_assignment_notification(
        email: str,
        title: str,
        deadline: str | None = None,
        language: str | None = None,
    ) -> bool:
        return EmailUtil.send(
            subject="New Assignment",
            recipients=[email],
            template="emails/assignment.html",
            context={
                "title": title,
                "deadline": deadline,
            },
            language=language,
        )

    @staticmethod
    def send_notification(
        email: str,
        subject: str,
        message: str,
        language: str | None = None,
    ) -> bool:
        return EmailUtil.send(
            subject=subject,
            recipients=[email],
            template="emails/notification.html",
            context={"message": message},
            language=language,
        )
