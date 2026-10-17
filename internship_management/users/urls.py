from django.contrib.auth import views as auth_views
from django.urls import path
from django.urls import reverse_lazy

# from .views import user_detail_view
# from .views import user_redirect_view
# from .views import user_update_view

from . import views

app_name = "users"

urlpatterns = [
    path("~redirect/", view=views.user_redirect_view, name="redirect"),
    path("~update/", view=views.user_update_view, name="update"),
    path("<int:pk>/", view=views.user_detail_view, name="detail"),

    path("", views.signup, name="signup"),
     path("otp/", views.otp, name="otp"),
    path("login/", views.login_view, name="login"),
    # Compatibility alias for existing templates and integrations that used allauth's name.
    path("login/", views.login_view, name="account_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="users/password_reset_request.html", email_template_name="users/password_reset_email.html", subject_template_name="users/password_reset_subject.txt", success_url=reverse_lazy("users:password_reset_done")), name="password_reset"),
    path("password-reset/sent/", auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"), name="password_reset_done"),
    path("password-reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html", success_url=reverse_lazy("users:password_reset_complete")), name="password_reset_confirm"),
    path("password-reset/complete/", auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"), name="password_reset_complete"),

]
