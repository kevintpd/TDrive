from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import ShareItemSerializer, JoinedListSerializer
from core.serializers import FileSerializer, FolderSerializer
from core.models import Folder, File, Item
from .models import ShareItem
from .utils import get_all_item_under
from core.permissions import ItemPermission
# Create your views here.
class MyShareListItemCreateView(generics.ListCreateAPIView):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        items = get_all_item_under(serializer.validated_data['Root'])
        serializer.save(Owner = self.request.user, Items = items)

class MyShareItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Owner=user))

class JoinedShareItemListView(generics.ListAPIView):
    serializer_class = JoinedListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Members = user))

class ShareFolderCreateView(generics.CreateAPIView):
    serializer_class = FolderSerializer
    #TODO 写权限，谁有权限创建
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        owner = ShareItem.objects.get(Id = self.kwargs['pk'])
        serializer.save(Owner = owner, Creator = self.request.user)


class ShareFileCreateView(generics.CreateAPIView):
    serializer_class = FileSerializer
    #TODO 写权限，谁有权限创建
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        owner = ShareItem.objects.get(Id=self.kwargs['pk'])
        serializer.save(Owner=owner, Creator=self.request.user)

class ShareFolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]

    def get_queryset(self):
        folderid = self.kwargs['pk']
        return Folder.objects.get_queryset(Q(Id = folderid))

class ShareFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]

    def get_queryset(self):
        fileid = self.kwargs['pk']
        return File.objects.get_queryset(Q(Id = fileid))