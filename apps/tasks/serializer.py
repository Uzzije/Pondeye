from rest_framework import serializers
from tasks.models import User, TikedgeUser


class UserAuthenticationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
