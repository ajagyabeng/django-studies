from rest_framework.decorators import api_view
from rest_framework.response import Response

from base.models import Room
from .serializers import RoomSerializer


@api_view(["GET"])
def getRoutes(request):
    """Shows all the routes available in the api"""
    routes = [
        "GET /api",
        "GET /api/rooms",
        "GET /api/rooms/:id"
    ]
    return Response(routes)


@api_view(["GET"])
def getRooms(request):
    """"""
    # many = True: Indicates if there will be manay objects to serialize or just one
    rooms = Room.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def getRoom(request, pk):
    """"""
    # many=False: Indicates there will be only one object to serialize.
    room = Room.objects.get(id=pk)
    serializer = RoomSerializer(room, many=False)
    print(serializer.data)
    return Response(serializer.data)
