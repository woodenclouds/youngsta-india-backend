from rest_framework import serializers



class SignupSerializers(serializers.Serializer):
    email =serializers.EmailField()
    name = serializers.CharField()
    password = serializers.CharField()


class VerifySerializers(serializers.Serializer):
    email =serializers.EmailField()
    otp =serializers.CharField()


class LoginSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password=serializers.CharField()