from django.apps import AppConfig


class TrainingConfig(AppConfig):
    name = "internship_management.training"

    def ready(self):
        import internship_management.training.signals