'''
Created on 24-07-2013

@author: kamil
'''
from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

from json_field.fields import JSONField

import tasks


class PushResult(models.Model):
    response_code = models.PositiveIntegerField(null=True, blank=True)
    
    def __unicode__(self):
        return u"({0}) {1}".format(self.response_code, self.scheduledpush)

class ScheduledPushManager(models.Manager):
    
    def create(self, policy, **kwargs):
        p = super(ScheduledPushManager, self).create(**kwargs)
        if p.send_at > p.scheduled_at:
            eta = p.send_at
        else:
            eta = p.scheduled_at
        tasks.push.apply_async(args=(policy, p.pk), eta=eta) #@UndefinedVariable

class PendingPushManager(models.Manager):
    
    def get_queryset(self):
        qs = super(PendingPushManager, self).get_queryset()
        return qs.filter(result__isnull=True)

class DeliveredPushManager(models.Manager):
    
    def get_queryset(self):
        qs = super(DeliveredPushManager, self).get_queryset()
        return qs.filter(result__isnull=False, result_response_code=200)

class CanceledPushManager(models.Manager):
    
    def get_queryset(self):
        qs = super(CanceledPushManager, self).get_queryset()
        return qs.filter(canceled_at__isnull=False)

class FailedPushManager(models.Manager):
    
    def get_queryset(self):
        qs = super(FailedPushManager, self).get_queryset()
        return qs.filter(result__isnull=False).exclude(result__status_code=200)
    

class ScheduledPush(models.Model):
    
    # some custom managers:
    objects = ScheduledPushManager()
    pending = PendingPushManager()
    delivered = DeliveredPushManager()
    canceled = CanceledPushManager()
    failed = FailedPushManager()
    
    scheduled_at = models.DateTimeField(auto_now_add=True)
    send_at = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)
    registration_id = models.CharField(max_length=4095)
    result = models.OneToOneField(PushResult, null=True, blank=True)
    attempt_no = models.PositiveSmallIntegerField(default=1)
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    source = generic.GenericForeignKey('content_type', 'object_id')
    
    data = JSONField()
    
    def __unicode__(self):
        if self.data['_list']:
            id_chunk = u'*'
        else:
            id_chunk = unicode(self.data['_id'])
        return u"{0}:{1}".format(self.data['_entity'], id_chunk)
        