from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.db.models import Q
from .models import Room, Topic, Message, User

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.


def loginPage(request):
    """
    authenticate: checks to make sure the credentials provided are correct. Returns a user object that matches the credentials or returns an error otherwise.
    """
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if user:
                user = authenticate(
                    request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    return redirect("home")
                else:
                    messages.error(request, "Incorrect Password.")
        except:
            messages.error(request, "User does not exist.")

    context = {"page": page}
    return render(request, "base/register_login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("home")


def registerPage(request):
    """
    commit=False: prevents the automatic commiting of the user into the database. This allows for any kind of manipulation that is needed before committing to database.
    """
    form = MyUserCreationForm()
    context = {"form": form}

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, "base/register_login.html", context)


def home(request):
    """
    objects: a model manager
    Q(): allows you to look up a keyword in various parts of a database
    """
    # Filter functionality by topics
    q = request.GET.get("q") if request.GET.get("q") != None else ''
    """
    q: gets the filter item passed into the request. If no filter item is passed, it is set to an empty string.

    filter(): returns all the items in the query when no filter parameter is passed into it.
    
    (topic__name__icontains=q): filters the topic by its name by checking if it contains the q.

    icontains: the 'i' makes it case-insensitive. Remove the 'i' and it becomes case-sensitive. There are other filter parameters(startswith, endswith, etc.)
    # rooms = Room.objects.filter(topic__name__startswith=q)
    # rooms = Room.objects.filter(topic__name__endswith=q)

    Q: makes the filter dynamic. Allows the filter to be applied on different columns/attributes of the model. In this instance, it allows the filter in the topic name, name of the room and description of the room.
    
    """
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    room_count = rooms.count()
    topics = Topic.objects.all()[0:4]

    """filter below filters the activity feed by room topic"""
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    """
    Renders a specific room.

    room.message_set.all(): gives the child object of the room in the messages model for a one to many relationship.

    room.participants.all(): gets all participants for a many to many relationship.
    """
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        """Process the comments from a room
        Message.objects.create(): creates an instance of the message object to be saved.
        """
        room_messages = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get("body")
        )
        """Add a user to the list of participants if they aren't already in it."""
        room.participants.add(request.user)
        return redirect("room", pk=room.id)

    context = {
        "room": room,
        "room_messages": room_messages,
        "participants": participants
    }
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    """login_required(login_url="login"): ensures onpy logged in users can access this view. Redirects them to the specified login_url"""
    form = RoomForm()

    topics = Topic.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description")
        )
        """
        get_or_create: checks for topic name and returns it in the topic object.
        topic: a topic object returned from the query.
        created: returns as False if topic name is found. Returns True and then goes ahead to create the new topic name if topic name is not found in the database.
        """
        # form = RoomForm(request.POST)
        # """passsing the request data into the RoomForm extracts the specific items in the request data and match it to the variouse fields."""
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        #     """form.save(): saves the form with the individual data filled in to the database"""
        return redirect("home")
    context = {
        "form": form,
        "topics": topics
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, pk):
    """
    instance=room: populates the form input fields with the info from the room to be update when the form is render in the html. 
    """
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    """Check to make sure user making the request to edit is same as the user who owns the room"""
    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.descrption = request.POST.get("description")
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # # instance as a parameter tells which room instance to update with received data.
        # if form.is_valid():
        #     form.save()
        return redirect("home")
    context = {
        "form": form,
        "topics": topics,
        "room": room
    }
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    """Check to make sure user making the request to delete is same as the user who owns the room"""
    if request.user != room.host:
        return HttpResponse("You are not allowed here!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room})


@login_required(login_url="login")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    """Check to make sure user making the request to delete is same as the user who owns the room"""
    if request.user != message.user:
        return HttpResponse("You are not allowed here!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message})


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context = {"form": form}

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", pk=user.id)

    return render(request, "base/update-user.html", context)


def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {"topics": topics}
    return render(request, "base/topics.html", context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {"room_messages": room_messages}
    return render(request, "base/activity.html", context)
