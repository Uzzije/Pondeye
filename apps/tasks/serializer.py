from rest_framework import serializers
from models import User, TikedgeUser


class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
