from django.apps import AppConfig


class AssignmentsConfig(AppConfig):
    name = "internship_management.submission"

    def ready(self):
        import internship_management.submission.signals