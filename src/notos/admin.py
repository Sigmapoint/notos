'''
Created on 22-07-2013

@author: kamil
'''
from django.contrib import admin

from .models import ScheduledPush, PushResult

admin.site.register(ScheduledPush)
admin.site.register(PushResult)
