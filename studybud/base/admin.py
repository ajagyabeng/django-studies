from django.contrib import admin

# Register your models here.

from .models import Room, Topic, Message, User

"""Register to allow the Room model to appear in the admin panel"""
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(User)
