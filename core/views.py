import mimetypes

from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404
from django.utils.encoding import escape_uri_path
# Create your views here.
from rest_framework import generics, status, permissions
from rest_flex_fields import FlexFieldsModelViewSet, is_expanded
from rest_framework.response import Response

from .models import File,Folder,Item
from .serializers import FileSerializer, FolderSerializer, ItemSerializer
from .permissions import ItemPermission
class FolderListView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return Folder.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        serializer.save(Owner = self.request.user, Creator = self.request.user)

class FolderRoot(generics.ListAPIView, FlexFieldsModelViewSet):
    permit_list_expands = ['Files', 'SubFolders']
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # for optimization purpose we prefetch expands area to reduce the database hits
        expands = [x for x in self.permit_list_expands if is_expanded(self.request, x)]
        if expands:
            return Folder.objects.filter(Q(Owner=user) & Q(ParentFolder=None)).prefetch_related(*expands)
        ##

        return Folder.objects.filter(Q(Owner=user) & Q(ParentFolder=None))

class FolderDetailView(generics.RetrieveUpdateDestroyAPIView, FlexFieldsModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return Folder.objects.filter(Q(Owner=user))

class FileListView(generics.ListCreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return File.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        print(self.request.data)
        serializer.save(Owner = self.request.user, Creator = self.request.user)

class FileSearchView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        searchWord = self.request.query_params["searchWord"]
        return File.objects.filter(Q(Owner = user) & (Q(Name__contains=searchWord.strip("\"")) | Q(FileTags__contains=searchWord.strip("\""))))

class FolderSearchView(generics.ListAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        searchWord = self.request.query_params["searchWord"]

        return Folder.objects.filter(Q(Owner=user) & Q(Name__contains=searchWord.strip("\"")))

class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return File.objects.filter(Q(Owner=user))

class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return Item.objects.filter(Owner=user)

class FileDownloadView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    def get(self, request, *args, **kwargs):
        file = get_object_or_404(File, pk=kwargs['id'])
        file_handle = file.FileData.open()
        mimetype, _ = mimetypes.guess_type(file.FileData.path)
        response = FileResponse(file_handle, content_type=mimetype)
        response['Content-Length'] = file.FileData.size
        response['Content-Disposition'] = f"attachment; filename={escape_uri_path(file.Name)}"
        return response

from .zip import make_tmp_archive
class FolderDownloadView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    def get(self, request, *args, **kwargs):
        folder = get_object_or_404(Folder, pk = kwargs['id'])
        response = make_tmp_archive(folder)
        if response is not None:
            return response
        else:
            content = {"msg": "not found"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)