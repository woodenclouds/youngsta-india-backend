from rest_framework import serializers
from accounts.models import UserProfile, Address


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
    
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)  # Assuming UserProfile can have multiple addresses

    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'email', 'country_code', 'phone_number', 'password',
                  'is_verified', 'device_token', 'address')