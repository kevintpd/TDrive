from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .serializers import ShareItemSerializer, JoinListSerializer
from core.serializers import FileSerializer, FolderSerializer
from core.models import Folder, File, Item
from .models import ShareItem
from .utils import get_all_item_under
from core.permissions import ItemPermission,ShareAddItemPermission
# Create your views here.
class ShareItemListView(generics.ListCreateAPIView):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ShareItem.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        items = get_all_item_under(serializer.validated_data['Root'])
        serializer.save(Owner = self.request.user, Items = items)

class MyShareDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Owner=user))

class JoinedShareListView(generics.ListAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Members = user))
class JoinShareView(generics.RetrieveUpdateAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShareItem.objects.all()
    def perform_update(self, serializer):
        shareitem = ShareItem.objects.get(Id = self.kwargs['pk'])
        shareitem.Members.add(self.request.user)
class AllShareListView(generics.ListAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShareItem.objects.all()

class ShareFolderCreateView(generics.CreateAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated, ShareAddItemPermission]

    def perform_create(self, serializer):
        shareitem = ShareItem.objects.get(Id = self.kwargs['pk'])
        serializer.save(Owner = shareitem.Owner, Creator = self.request.user)
        shareitem.Items.add(serializer.instance)
class ShareFileCreateView(generics.CreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, ShareAddItemPermission]

    def perform_create(self, serializer):
        shareitem = ShareItem.objects.get(Id=self.kwargs['pk'])
        serializer.save(Owner=shareitem.Owner, Creator=self.request.user)
        shareitem.Items.add(serializer.instance)
    def create(self, request, *args, **kwargs):

        super().create(self, request, *args, **kwargs)

class ShareFolderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    queryset = Folder.objects.all()

class ShareFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    queryset = File.objects.all()