'''
Created on 25-07-2013

@author: kamil
'''
import logging

import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import utc
from models import ScheduledPush

class BasePushPolicy:
    
    ALLOWED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]
    MAX_RETRIES = 5
    
    @classmethod
    def registration_id_changed(cls, previous_id, current_id):
        msg = "Registration id %s changed to %s"
        logging.getLogger(__name__).warning(msg, previous_id, current_id)
    
    @classmethod
    def registration_id_revoked(cls, revoked_id):
        msg = "Registration id %s was revoked"
        logging.getLogger(__name__).warning(msg, revoked_id)
    
    @classmethod
    def should_retry(cls, scheduled_push, push_result):
        return scheduled_push.attempt_no <= cls.MAX_RETRIES
    
    def __init__(self, view, request, response):
        self.view = view
        self.request = request
        self.response = response
    
    def on_post(self):
        return ({}, [], "update")
    
    def on_put(self):
        return ({}, [], "update")
    
    def on_patch(self):
        return ({}, [], "update")
    
    def on_delete(self):
        return ({}, [], "delete")
    
    def get_entity_id(self, reg_id):
        try:
            obj = self.view.object
        except AttributeError:
            obj = None
        try:
            qs = self.view.qs
        except AttributeError:
            qs = None
        if object:
            ct = ContentType.objects.get_for_model(
                obj,
                for_concrete_model=True
            )
            app_label = ct.app_label
            classname = self.view.object.__class__.__name__
            entity_id = u".".join([app_label, classname])
        elif qs:
            ct = ContentType.objects.get_for_model(
                qs.model,
                for_concrete_model=False
            )
            app_label = ct.app_label
            classname = self.view.queryset.model.__name__
            entity_id = u".".join([app_label, classname])
        else:
            entity_id = None
        return entity_id
    
    def get_has_many(self, reg_id):
        try:
            obj = self.view.object
        except AttributeError:
            obj = None
        try:
            qs = self.view.qs
        except AttributeError:
            qs = None
        if obj:
            return False
        elif qs:
            return True
        else:
            return None
    
    def get_obj(self, reg_id):
        try:
            obj = self.view.object
        except AttributeError:
            obj = None
        return obj
    
    def get_id(self, reg_id):
        obj = self.get_obj()
        if obj:
            return obj.id
        else:
            return None
    
    def get_datetime(self, reg_id):
        return datetime.datetime.utcnow().replace(tzinfo=utc)
    
    def finalize_data(self, data, date_time, action, reg_id):
        entity_id = self.get_entity_id()
        id = self.get_id() #@ReservedAssignment
        list = self.get_has_many() #@ReservedAssignment
        url = self.get_url()
        finalized = dict(data.items())
        finalized.update({
            "_entity": entity_id,
            "_id": id,
            "_url": url,
            "_datetime": date_time.isoformat(),
            "_list": list,
            "_action": action,
        })
        return finalized
    
    def get_url(self, reg_id):
        obj = self.get_obj()
        try:
            return obj.get_absolute_url()
        except AttributeError:
            return None
    
    def trigger(self):
        if not 200 <= self.response.status_code < 300:
            return
        if self.request.method in self.__class__.ALLOWED_METHODS:
            suffix = self.request.method.lower()
            callback = getattr(self, 'on_' + suffix)
            data, registration_ids, action = callback()
            for reg_id in registration_ids:
                date_time = self.get_datetime(reg_id)
                finalized_data = self.finalize_data(data, date_time, action, reg_id)
                ScheduledPush.objects.create(
                    self.__class__,
                    send_at=datetime.datetime.utcnow().replace(tzinfo=utc),
                    registration_id=reg_id,
                    source=self.get_obj(reg_id),
                    data=finalized_data
                )