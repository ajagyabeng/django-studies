from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    # Tell django to use email to login instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(
        User, related_name="participants", blank=True)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Sets the order in which the model arranges the the query items returned.
        Appending '-' to the items in the list orders the query items in descending order.

        Orders by the most updated using the date created. This applies to all querries that is maade to the class instead of putting order_by() on each query.
        """
        ordering = ["-update", "-created"]

    def __str__(self):
        """Creates a string representation of the Room class"""
        return self.name

    """
    blank keyword: when form is submitted, the field for description can be empty/blank

    auto_now: takes a timestamp of when a save method is called to update database table.

    auto_now_add: takes a timestamp of when an instance was first created.

    topic: In case the topic class is below the room class, put the Topic in qoutes like "Topic" when specifying the foreign key.
    """


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        """
        ordering = ["-update", "-created"]

    def __str__(self):
        """Creates a string representation of the Room class"""
        return self.body[0:50]  # previews the first 50 characters

    """
    on_delete: tells the model what to do when the parent model is delete. Cascade means all the messages will also be deleted.
    """
