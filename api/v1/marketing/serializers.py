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

class AddCoupenSerializer(serializers.ModelSerializer):
    offer = serializers.IntegerField( required=False)
    description = serializers.CharField()
    validity = serializers.DateField() 
    class Meta:
        model = Coupens
        fields = ('offer', 'description', 'validity')

class CoupenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupens
        fields = (
            'id',
            'code',
            'offer',
            'description',
            'validity',
            'offer_price',
            'offer_start_price',
            'offer_end_price',
        )


class BannerSerializer(serializers.Serializer):
    section = serializers.CharField()
    slider = serializers.BooleanField()
    items = serializers.ListField()


class BannerViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banners
        fields = '__all__'

class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerItems
        fields = '__all__'


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = "__all__"