from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
