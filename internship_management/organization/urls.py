from django.urls import path

from . import views

app_name = "organization"

urlpatterns = [
    path("", views.invitation_list, name="invitation_list"),
    path("create/", views.invitation_create, name="invitation_create"),
    path("<uuid:invitation_id>/", views.invitation_detail, name="invitation_detail"),
    path("<uuid:invitation_id>/resend/", views.invitation_resend, name="invitation_resend"),
    path("<uuid:invitation_id>/revoke/", views.invitation_revoke, name="invitation_revoke"),
]

public_urlpatterns = [
    path("<str:token>/", views.invitation_accept, name="invitation_accept"),
    path("<str:token>/setup/", views.invitation_setup, name="invitation_setup"),
]

urlpatterns += public_urlpatterns
