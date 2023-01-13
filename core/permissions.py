from rest_framework import permissions
from django.utils import timezone
from shareapi.models import ShareItem
from django.db.models import Q
class ItemPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user == obj.Owner:
            return True
        queryset = ShareItem.objects.filter(Q(Members = request.user) & (Q(OutdatedTime__gt = timezone.now() | Q(OutdatedTime = None)) & Q(Items = obj)))
        queryset_type1 = queryset.filter(ShareType=1)

        match request.method:
            case 'GET':
                if queryset.exists():
                    return True
            case 'DELETE':
                if hasattr(obj, "drive_folder") and obj.Creator == request.user and len(obj.Files.all())==0 and queryset_type1.exists():
                    return True
                if hasattr(obj, "drive_file") and obj.Creator == request.user and queryset_type1.exists():
                    return True
            case 'PUT':
                if obj.Creator == request.user and queryset_type1.exists():
                    return True
        return True