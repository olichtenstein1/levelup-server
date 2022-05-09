"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Game
from levelupapi.models.gamer import Gamer
from levelupapi.models.gametype import GameType
from django.core.exceptions import ValidationError

class GameView(ViewSet):
    """Level up game view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game"""
        
        game = Game.objects.get(pk=pk)
        serializer = GameSerializer(game)
        return Response(serializer.data)
        
        """Returns:
            Response -- JSON serialized game
        """
        
        

    def list(self, request):
        """Handle GET requests to get all games"""
        
        games = Game.objects.all()
        
        game_type = request.query_params.get('type', None)
        if game_type is not None:
            games = games.filter(game_type_id=game_type)
        
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

        """Returns:
            Response -- JSON serialized list of games
        """
        
    def create(self, request):
       
        """Handle POST operations

        Returns:
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(gamer=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """
        game = Game.objects.get(pk=pk)
        serializer = CreateGameSerializer(game, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk):
        game = Game.objects.get(pk=pk)
        game.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
        


class GameSerializer(serializers.ModelSerializer):
    """JSON serializer for games
    """
    class Meta:
        model = Game
        fields = ('id', 'title', 'maker', 'number_of_players', 'skill_level', 'game_type', 'gamer')
        depth = 1
        
class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker', 'number_of_players', 'skill_level', 'game_type']