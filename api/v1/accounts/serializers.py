from rest_framework import serializers
from accounts.models import UserProfile, Address, Staff


class SignupSerializers(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

class AdminSignupSerializers(serializers.Serializer):
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
   # address = AddressSerializer(many=True, read_only=True)  # Assuming UserProfile can have multiple addresses

    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name', 'email', 'country_code', 'phone_number', 'password')


class AddStaffSerializer(serializers.Serializer):
    fullname = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()
    type = serializers.CharField()


class StaffSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField()
    email = serializers.CharField()
    type = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = Staff
        fields = ('fullname', 'email', 'password', 'type')


class ViewStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('id',
                  'fullname',
                  'email',
                  'type'
                  )
        
    
