from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

from .models import Room, User


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", "password1", "password2"]


class RoomForm(ModelForm):
    class Meta:
        """
        __all__: this looks into the Model in consideration and creates fields for all of its specified attributes.

        A list of fields could also be specified.

        exclude: Excludes the specified items from being rendered as part of the form.
        """
        model = Room
        fields = '__all__'
        exclude = ["participants", "host"]


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["name", "username", "email", "avatar", "bio"]
