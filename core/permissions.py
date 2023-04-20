from rest_framework import permissions
from django.utils import timezone
from shareapi.models import ShareItem
from django.db.models import Q


class ItemPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user == obj.Owner:
            return True
        queryset = ShareItem.objects.filter(
            Q(Members=request.user) & (Q(OutdatedTime__gt=timezone.now()) | Q(OutdatedTime=None)) & Q(Items=obj))
        queryset_type1 = queryset.filter(ShareType=1)
        print(queryset)
        print(ShareItem.objects.filter(Q(Items=obj)))
        if request.method == 'GET':
            if queryset.exists():
                return True
        elif request.method == 'DELETE':
            if hasattr(obj, "drive_folder") and obj.Creator == request.user and len(
                    obj.Files.all()) == 0 and queryset_type1.exists():
                return True
            if hasattr(obj, "drive_file") and obj.Creator == request.user and queryset_type1.exists():
                return True
        elif request.method == 'PUT':
            if obj.Creator == request.user and queryset_type1.exists():
                return True
        else:
            return False



class ShareAddItemPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if ShareItem.objects.get(Id=view.kwargs['pk']).Owner == request.user:
            return True

        queryset = ShareItem.objects.filter(Q(Id=view.kwargs['pk']) & Q(ShareType=1) & Q(Members=request.user)
                                            & (Q(OutdatedTime__gt=timezone.now()) | Q(OutdatedTime=None)))
        if queryset.exists():
            return True
