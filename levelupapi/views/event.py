"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event
from levelupapi.models.game import Game
from levelupapi.models.gamer import Gamer
from django.core.exceptions import ValidationError
from rest_framework.decorators import action




class EventView(ViewSet):
    """Level up event view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single event"""
        
        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)
        
        """Returns:
            Response -- JSON serialized event
        """
        
        

    def list(self, request):
        """Handle GET requests to get all events"""
        
        events = Event.objects.all()
        gamer = Gamer.objects.get(user=request.auth.user)
        
        
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)
            
        # Set the `joined` property on every event
        for event in events:
            # Check to see if the gamer is in the attendees list on the event
            event.joined = gamer in event.attendees.all()

                   
        
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

        """Returns:
            Response -- JSON serialized list of events
        """
        
    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized game instance
        """
        organizer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(organizer=organizer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a event

        Returns:
            Response -- Empty body with 204 status code
        """
        event = Event.objects.get(pk=pk)
        serializer = CreateEventSerializer(event, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
    
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.attendees.add(gamer)
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    
    @action(methods=['post'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to leave an event"""
        
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.attendees.remove(gamer)
        return Response({'message': 'Gamer dismissed'}, status=status.HTTP_200_OK)
        
    

class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events
    """
    class Meta:
        model = Event
        fields = ('id', 'description', 'date', 'time', 'game', 'organizer', 'attendees', 'joined')
        depth = 2
        
class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'description', 'date', 'time', 'game']