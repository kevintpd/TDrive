from rest_flex_fields import FlexFieldsModelSerializer

from .models import ShareItem
class ShareItemSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ShareItem
        fields = ['Id', 'Owner', 'Items', 'Root', 'CreatedTime', 'OutdatedTime', 'Members', 'Code', 'ShareType']
        extra_kwargs = {
            'CreatedTime': {'read_only': True},
            'Id': {'read_only': True},
        }
class JoinedListSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = ShareItem
        fields = ['Owner', 'Root', 'CreatedTime', 'OutdatedTime', 'Members', 'ShareType']
        extra_kwargs = {
            'Owner': {'read_only': True},
            'Root': {'read_only': True},
            'CreatedTime': {'read_only': True},
            'OutdatedTime': {'read_only': True},
            'Members': {'read_only': True},
        }