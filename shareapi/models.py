import string
import uuid
import random
from django.db import models
from django.utils.datetime_safe import datetime

from core.models import Item, Folder


# Create your models here.
class ShareItem(models.Model):
    """
    关于文件/文件夹共享的一些想法：
    1.在哪里可以看到？
    系统分为三个部分：自己的文件、自己共享的文件夹（文件）、自己加入的文件夹（文件）
    2.怎么判断？
    共享文件夹可以通过判断request.user==Share.Item.Owner来判断，加入的共享可以根据request.user_in = Share.AccessUser
    3.权限怎么弄？（如何下载和上传）
    ①文件下载
    request.user_in = ShareItem.AccessUser ， 已经登录
    ②文件上传
    ③文件夹下载
    request.user_in = ShareItem.AccessUser ， 已经登录
    ④子文件夹创建

    目前百度网盘的贡献文件夹做法：
    1.所有加入的用户都能查看、上传、下载所有的文件，然后Owner能移除成员（控制成员）
    2.成员A在Owner创建的文件夹下创建了子文件夹，那成员B可以查看、下载、上传，但不能删除A创建的子文件夹。Owner能删除（理解成A创建的子文件夹是在Owner的文件夹之下的）
    3.接着2讲，那是否可以把权限做成这样：所有成员可以查看、下载、上传，但是删除的权限在子文件夹的创建者及其父辈祖宗那里

    讨论结果：2023.1.12
    1.所有成员都可以查看，下载，上传文件
    2.所有成员都可以创建，修改空文件夹
    3.所有成员都可以修改删除自己上传的文件
    4.非空文件夹以及所有东西的删除权限只有share的owner有
    """
    Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # 因为是m2m，所以这里要单独做一个owner字段，用于标识是share的，在文件非共享之后，回到Owner的文件夹下
    Owner = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='CreatedShares')
    # 这里可以通过hasattr(Folder/File/Item,'shared')来判断这个东西是否被共享了，那我的共享obj怎么查就可以解决了
    Items = models.ManyToManyField(Item, related_name='shares')
    # 来确定哪个是分享的根文件夹
    Root = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='RelatedShares')
    CreatedTime = models.DateTimeField(auto_now=True)
    OutdatedTime = models.DateTimeField(blank=True, null=True)
    # 这里可以通过request.user.JoinedShares 来获取自己所加入的所有的共享obj，那我加入的共享怎么查就可以解决了
    Members = models.ManyToManyField('accounts.User', blank=True, related_name='JoinedShares')
    Code = models.CharField(max_length=8, default=None)
    Description = models.CharField(max_length=100,default=None)

    class ShareTypeChoices(models.IntegerChoices):
        Public = 1
        Selective = 2

    ShareType = models.IntegerField(choices=ShareTypeChoices.choices)

    def save(self, *args, **kwargs):
        if self.Code is None or "":
            self.Code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
        super().save(*args, **kwargs)
