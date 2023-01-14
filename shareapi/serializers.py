from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from core.models import Item
from .models import ShareItem
class ShareItemSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ShareItem
        fields = ['Id', 'Owner', 'Items', 'Root', 'CreatedTime', 'OutdatedTime', 'Members', 'Code', 'ShareType', 'Description']
        extra_kwargs = {
            'CreatedTime': {'read_only': True},
            'Id': {'read_only': True},
            'Items': {'read_only': True},
            'Owner': {'read_only': True},
        }

    def validate_Root(self, Root):
        if self.instance is None:
            if self.context['request'].user != Root.Owner:
                raise serializers.ValidationError("the item is not yours")
            return Root
        else:
            return Root

class JoinListSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ShareItem
        fields = ['Id', 'Owner', 'Root', 'CreatedTime', 'OutdatedTime', 'Members', 'ShareType', 'Description']
        extra_kwargs = {
            'Id': {'read_only': True},
            'Owner': {'read_only': True},
            'Root': {'read_only': True},
            'CreatedTime': {'read_only': True},
            'OutdatedTime': {'read_only': True},
            # 'Members': {'read_only': True},
            'ShareType': {'read_only': True},
            'Description': {'read_only': True},
        }