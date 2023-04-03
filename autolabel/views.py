from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from TDrive.settings import AUTO_LABEL_TIME
from .AutoLabelFunc import AutoLabelProcess
from core.models import File

import time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_job
# 实例化调度器
scheduler = BackgroundScheduler(timezone='Asia/Shanghai') # 这个地方要加上时间，不然他有时间的警告
# 调度器使用DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), "default")
@register_job(scheduler, "cron", hour=20, minute=46 ,second = 00,replace_existing=True)
def job1():
    print("开始执行自动标签功能")
    files = File.objects.filter(IsImage__exact=True)
    for file in files:
        if "|" not in file.FileTags:
            file_auto_tags = AutoLabelProcess("media/"+file.Hash+"."+file.Name.split(".")[-1])
            if file_auto_tags[0][1]>75:
                print("大于75的概率，一个标签."+"\n图片名称："+file.Name+"\n标签："+file_auto_tags[0][0])
                File.objects.filter(pk = file.pk).update(FileTags = file.FileTags+"|"+file_auto_tags[0][0])
            else:
                print("取前两个标签."+"\n图片名称："+file.Name+"\n标签："+file_auto_tags[0][0]+"\n"+file_auto_tags[1][0])
                File.objects.filter(pk=file.pk).update(FileTags = file.FileTags+"|"+file_auto_tags[0][0]+"|"+file_auto_tags[1][0])

try:
    scheduler.start()
except Exception as e:
    print(e)
    # 有错误就停止定时器
    scheduler.shutdown()

