from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from .models import Item, File, Folder

class ItemSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class FileSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = File
        fields = ['Id', 'Name', 'Owner', 'Creator', 'DateUpload', 'Hash', 'FileData', 'FileType', 'FileSize', 'IsImage', 'FileTags', 'ParentFolder']

        extra_kwargs = {

            'Owner': {'read_only': True},
            'Creator': {'read_only': True},
            'Hash': {'read_only': True},
            'FileSize': {'read_only': True},
            'IsImage': {'read_only': True, 'required': False},
            'FileTags': {'read_only': True, 'required': False},
            'FileData': {'required': False},
            'Name': {'required': False},
        }

class FolderSerializer(FlexFieldsModelSerializer):

    def check_looped_folder(self, ParentFolder):
        if ParentFolder is None:
            return
        if ParentFolder == self.instance:
            raise serializers.ValidationError('Folder Dependency Is In Loop')
        if ParentFolder.ParentFolder is not None:
            self.check_looped_folder(ParentFolder.ParentFolder)

    def validate_ParentFolder(self, ParentFolder):
        if self.instance is not None and ParentFolder == self.instance:
            raise serializers.ValidationError('Parent Folder Is Not Allowed To Be Self')
        self.check_looped_folder(ParentFolder)
        return ParentFolder

    class Meta:
        model = Folder
        fields = ['Id', 'Name', 'Owner', 'Creator', 'ParentFolder', 'SubFolders', 'Files', 'DateCreated', 'DateModified']
        extra_kwargs = {
            'Owner': {'read_only': True},
            'Creator': {'read_only': True},
            'Files': {'read_only': True},
            'Id': {'read_only': True},
            'SubFolders': {'read_only': True},
            'DateCreated': {'read_only': True},
            'DateModified': {'read_only': True},
        }

    expandable_fields = {
        'Files': (FileSerializer, {'many': True}),
        'SubFolders': ('core.FolderSerializer', {'many': True})
    }