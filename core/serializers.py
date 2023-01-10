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
        fields = ['Id', 'Name', 'Owner', 'DateUpload', 'Hash', 'FileData', 'FileExtension', 'FileSize', 'IsImage', 'FileTags', 'ParentFolder']

        extra_kwargs = {

            'Owner': {'read_only': True},
            'FileExtension': {'read_only': True, 'required': False},
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
        fields = ['Id', 'Name', 'Owner', 'ParentFolder', 'SubFolders', 'Files', 'DateCreated', 'DateModified']
        extra_kwargs = {
            'Id': {'read_only': True},
            'SubFolders': {'read_only': True},
            'DateCreated': {'read_only': True},
            'DateModified': {'read_only': True},
        }

    expandable_fields = {
        'Files': (FileSerializer, {'many': True}),
        'SubFolders': ('core.FolderSerializer', {'many': True})
    }
