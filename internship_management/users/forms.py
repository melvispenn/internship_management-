# from allauth.account.forms import SignupForm
# from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from .models import User

from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "autocomplete": "email",
                "class": "auth-input",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
                "class": "auth-input",
            }
        ),
    )


class SignupForm(forms.ModelForm):
      
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Create a password",
                "autocomplete": "new-password",
                "class": "auth-input",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password",
                "autocomplete": "new-password",
                "class": "auth-input",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("name", "email")

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The passwords do not match."
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user
    
    # def clean(self):
    #     cleaned_data = super().clean()

    #     email = cleaned_data.get("email")
    #     password = cleaned_data.get("password")

    #     if email and password:
    #         self.user = authenticate(
    #             email=email,
    #             password=password,
    #         )

    #         if self.user is None:
    #             raise forms.ValidationError(
    #                 "Invalid email or password."
    #             )

    #     return cleaned_data

    def get_user(self):
        return self.user

class OTPForm(forms.Form):
    code = forms.CharField(
        label="OTP Code",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter the 6-digit code",
                "autocomplete": "one-time-code",
                "class": "auth-input text-center text-2xl font-bold tracking-[0.5em]",
            }
        ),
    )

    
class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}

class UserAdminCreationForm(admin_forms.AdminUserCreationForm):

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {
                "unique": _("This email has already been taken."),
            },
        }

# class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
#     """
#     Form for User Creation in the Admin Area.
#     To change user signup, see UserSignupForm and UserSocialSignupForm.
#     """

#     class Meta(admin_forms.UserCreationForm.Meta):
#         model = User
#         fields = ("email",)
#         field_classes = {"email": EmailField}
#         error_messages = {
#             "email": {"unique": _("This email has already been taken.")},
#         }


# class UserSignupForm(SignupForm):
#     """
#     Form that will be rendered on a user sign up section/screen.
#     Default fields will be added automatically.
#     Check UserSocialSignupForm for accounts created from social.
#     """


# class UserSocialSignupForm(SocialSignupForm):
#     """
#     Renders the form when user has signed up using social accounts.
#     Default fields will be added automatically.
#     See UserSignupForm otherwise.
#     """
