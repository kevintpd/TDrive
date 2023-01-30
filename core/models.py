import hashlib
import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User

from .storage import OverwriteStorage, GetHashName
# Create your models here.

class Item(models.Model):
    Id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #名称
    Name = models.CharField(max_length=256, default=None)
    #拥有者
    Owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="items")
    #创建者
    Creator = models.ForeignKey(User, on_delete=models.CASCADE)
    @property
    def size(self):
        #判断Item类的子类是否是file
        if hasattr(self, 'drive_file'):
            return self.drive_file.file_size
        #判断Item类的子类是否是folder
        elif hasattr(self, 'drive_folder'):
            return self.drive_folder.size
        else:
            return 0

    def has_parent(self, pid):
        if self.pk == pid:
            return True
        else:
            if hasattr(self, 'drive_file'):
                loc = self.drive_file.location
            elif hasattr(self, 'drive_folder'):
                loc = self.drive_folder.location
        return loc.has_parent(pid)

class File(Item):
    class Meta:
        default_related_name = "drive_file"

    #借用JDrive的代码，存储为哈希值，并且数据库中不重复存储
    FileData = models.FileField(upload_to=GetHashName, storage=OverwriteStorage)
    #文件拓展，这里我不知道为什么他要写CharFiled，是否有自动识别的代码，然后添加文件类型
    # FileExtension = models.CharField(max_length=10)
    #这个也不是很懂，后面再看吧。
    #在序列化的时候要注意，这个是不需要序列化的，是在反序列化的时候自动生成的
    FileType = models.CharField(max_length=20, default=None)
    #应该有计算文件大小的代码
    FileSize = models.DecimalField(
        max_digits=10, decimal_places=3, default=None
    )
    # #先放在这里吧
    # TempFileId = models.UUIDField(blank=True, null=True)
    #判断是否为照片
    IsImage = models.BooleanField(blank=False, default=False)
    #文件夹标签，这里用字符串来代替列表，用,来隔开，使用的时候再用一个split分开
    FileTags = models.CharField(max_length=200, default=None)
    #文件的位置
    ParentFolder = models.ForeignKey(
        "Folder", on_delete=models.CASCADE, related_name="Files"
    )
    # 上传日期
    DateUpload = models.DateTimeField(blank=False, auto_now_add=True, editable=False)
    Hash = models.CharField(max_length=64, default=None)
    ItemType = models.CharField(max_length=10, default="File")

    def save(self, *args, **kwargs):
        """
        计算并保存file_type、isimage、file_tags
        """
        if self.Hash is None:
            data_bytes = self.FileData.read()
            self.Hash = hashlib.sha256(data_bytes).hexdigest()

        if self.Name is None or '':
            self.Name = self.FileData.name
        if self.FileSize is None:
            self.FileSize = self.FileData.size

        try:
            self.FileType = self.Name.split('.')[-1] if '.' in self.Name else self.Name
        except:
            self.FileType = None
        try:
            self.IsImage = True if self.Name.split('.')[-1].upper() in ['JPEG', 'JPG', 'PNG'] else False
        except:
            self.IsImage = False
        try:
            self.FileTags = self.Name.split('.')[0]
        except:
            self.FileTags = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Name



class Folder(Item):
    class Meta:
        default_related_name = "drive_folder"

    #因为一个文件夹可能会有很多的子文件夹，所以这里用外键
    ParentFolder = models.ForeignKey(
        "Folder",
        on_delete=models.CASCADE,
        related_name="SubFolders",
        null=True,
    )
    # 创建日期
    DateCreated = models.DateTimeField(blank=False, auto_now_add=True)
    # 修改日期
    DateModified = models.DateTimeField(auto_now=True)
    ItemType = models.CharField(max_length=10, default="Folder")

    @property
    def size(self):
        return sum(map(lambda x: x.size, self.SubFolders.all())) + sum(
            map(lambda x: x.file_size, self.Files.all())
        )

    @property
    def urlpath(self):
        folder = self
        path = []
        while folder.location is not None:
            path.append(str(folder.name))
            folder = folder.location
        return "/".join(path[::-1])


    def __str__(self):
        return self.Name

#在保存User模型成功之后，调用该函数，创建根文件夹
@receiver(post_save, sender=User)
def create_drive(sender, instance, created, **kwargs):
    if created:
        drive = Folder.objects.create(
            Name="root",
            Owner=instance,
            ParentFolder=None,
            Creator=instance,
        )
        instance.root_drive = drive
        instance.save()