from django.db.models import Q
from django.shortcuts import render


# Create your views here.
from rest_framework import generics
from rest_flex_fields import FlexFieldsModelViewSet

from .models import File,Folder,Item
from .serializers import FileSerializer, FolderSerializer

class FolderListView(generics.ListCreateAPIView):
    serializer_class = FolderSerializer

    def get_queryset(self):
        user = self.request.user.pk
        return Folder.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        serializer.save(Owner = self.request.user)

class FolderDetailView(generics.RetrieveUpdateDestroyAPIView, FlexFieldsModelViewSet):
    serializer_class = FolderSerializer

    def get_queryset(self):
        user = self.request.user.pk
        return Folder.objects.filter(Q(Owner=user))

class FileListView(generics.ListCreateAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        user = self.request.user.pk
        return File.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        serializer.save(Owner = self.request.user)

class FileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        user = self.request.user.pk
        return File.objects.filter(Q(Owner=user))