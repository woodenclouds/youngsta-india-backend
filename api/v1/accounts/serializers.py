from rest_framework import serializers
from accounts.models import *


class SignupSerializers(serializers.Serializer):
    # name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

class AdminSignupSerializers(serializers.Serializer):
    # name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()



class VerifySerializers(serializers.Serializer):
    email =serializers.EmailField()
    otp =serializers.CharField()


class LoginSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password=serializers.CharField()


class ViewCostomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'first_name',
            'last_name',
            'created_at',
            'email',
            'phone_number',

        )