from rest_framework import serializers



class SignupSerializers(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()



class VerifySerializers(serializers.Serializer):
    email =serializers.EmailField()
    otp =serializers.CharField()


class LoginSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password=serializers.CharField()