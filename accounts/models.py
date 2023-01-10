import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
#继承自AbstractUser 添加一些自己的属性，然后在setting中更改系统使用的User模型，使其与系统认证匹配
class User(AbstractUser):
    root_drive = models.OneToOneField('core.Folder',
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='root_drive')
    def __str__(self):
        return self.username

class RegisterInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(editable=False, blank=False, unique=True)
    create_time = models.DateTimeField(auto_now=True)
