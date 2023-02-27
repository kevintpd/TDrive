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
from rest_flex_fields import FlexFieldsModelViewSet, is_expanded
# Create your views here.
class ShareItemListView(generics.ListCreateAPIView):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ShareItem.objects.filter(Q(Owner = user))

    def perform_create(self, serializer):
        items = get_all_item_under(serializer.validated_data['Root'])
        Folder.objects.filter(Id = serializer.validated_data['Root'].Id).update(IsShared = True)
        serializer.save(Owner = self.request.user, Items = items)


class ShareItemRootListView(generics.ListAPIView, FlexFieldsModelViewSet):
    permit_list_expands = ['Root','Owner','Members']
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        expands = [x for x in self.permit_list_expands if is_expanded(self.request, x)]
        if expands:
            return ShareItem.objects.filter(Q(Owner=user)).prefetch_related(*expands)
        return ShareItem.objects.filter(Q(Owner = user))
class MyShareDetailView(generics.RetrieveUpdateDestroyAPIView,FlexFieldsModelViewSet):
    serializer_class = ShareItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user.pk
        return ShareItem.objects.filter(Q(Owner=user))

    def destroy(self, request, *args, **kwargs):
        shareitemId = self.kwargs['pk']
        rootFolderId = ShareItem.objects.get(pk=shareitemId).Root.Id
        a = ShareItem.objects.filter(Root=rootFolderId).count()
        if a == 1:
            Folder.objects.filter(Id=rootFolderId).update(IsShared=False)
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, *args, **kwargs):
        print(request.data)
        return super().put(request, *args, **kwargs)


class JoinedShareListView(generics.ListAPIView, FlexFieldsModelViewSet):
    permit_list_expands = ['Root', 'Owner', 'Members']
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        expands = [x for x in self.permit_list_expands if is_expanded(self.request, x)]
        if expands:
            return ShareItem.objects.filter(Q(Members=user)).prefetch_related(*expands)
        return ShareItem.objects.filter(Q(Members=user))

class RefreshShareListView(generics.ListAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        a = ShareItem.objects.filter(Q(Members=user))
        for shareitem in a:
            item = get_all_item_under(Folder.objects.filter(pk = shareitem.Root.Id)[0])
            ShareItem.objects.filter(pk = shareitem.pk)[0].Items.add(*item)
        return ShareItem.objects.filter(Q(Members=user))

class JoinShareView(generics.RetrieveUpdateAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShareItem.objects.all()
    def perform_update(self, serializer):
        shareitem = ShareItem.objects.get(Id = self.kwargs['pk'])
        shareitem.Members.add(self.request.user)


class QuitShareView(generics.RetrieveUpdateAPIView):
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShareItem.objects.all()
    def perform_update(self, serializer):
        shareitem = ShareItem.objects.get(Id = self.kwargs['pk'])
        shareitem.Members.remove(self.request.user)
class AllShareListView(generics.ListAPIView,FlexFieldsModelViewSet):
    permit_list_expands = ['Root', 'Owner', 'Members']
    serializer_class = JoinListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        expands = [x for x in self.permit_list_expands if is_expanded(self.request, x)]
        if expands:
            return ShareItem.objects.filter(~Q(Members__in = [self.request.user])).prefetch_related(*expands)
        return ShareItem.objects.filter(~Q(Members__in = [self.request.user]))

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
class ShareFolderDetailView(generics.RetrieveUpdateDestroyAPIView, FlexFieldsModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    queryset = Folder.objects.all()

    def get_queryset(self):

        return super().get_queryset()


class SearchShareFileView(generics.ListAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        searchWord = self.request.query_params["searchWord"]
        shareItem = ShareItem.objects.filter(Members= user)
        file_all_list = []
        for shareitem in shareItem:
            for item in shareitem.Items.all():
                if hasattr(item, 'drive_file'):
                    file_all_list.append(item.Id)
        return File.objects.filter(Q(Id__in = file_all_list) & Q(Name__contains=searchWord.strip("\"")))
class ShareFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated, ItemPermission]
    queryset = File.objects.all()