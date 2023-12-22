from rest_framework import serializers
from marketing.models import *
from django.db.models import Sum



class AdsItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdsItem
        fields = [
             'advertisement', 
             'title' ,
             'position',
             'url', 
             'image', 
        ]



class AdsSerializer(serializers.ModelSerializer):
    ad_items = AdsItemSerializer(many=True, read_only=True)

    class Meta:
        model = Ads
        fields = ['id', 'title', 'position', 'heading', 'subheading', 'ad_items']
