'''
Created on 31-07-2013

@author: kamil
'''
import logging
import sys
import datetime

from celery import task

from gcmclient import GCM, JSONMessage
from gcmclient.gcm import GCMAuthenticationError

from django.conf import settings
from django.utils.timezone import utc

GCM_URL = settings.DDCS['GCM_URL']
API_KEY = settings.DDCS['GCM_API_KEY']
gcm = GCM(API_KEY, GCM_URL)

@task
def push(policy, pk):
    from notos.models import ScheduledPush
    from notos.models import PushResult
    try:
        sp = ScheduledPush.pending.get(pk=pk)
    except ScheduledPush.DoesNotExist:
        msg = u"No scheduled push with pk=%d was found in task."
        logging.getLogger(__name__).info(msg, pk, exc_info=sys.exc_info())
        return
    # hack, we need custom JSON Decoder
    safe_data = {}
    for k, v in sp.data.items():
        if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
            safe_data[k] = v.isoformat()
        else:
            safe_data[k] = v
    sp.data.update({'_datetime': sp.data['_datetime'].isoformat()})
    safe_data.update(sp.data)
    message = JSONMessage([sp.registration_id], safe_data)
    try:
        results = gcm.send(message)
        status_code = 200
    except GCMAuthenticationError:
        msg = u"GCM authentication failed."
        logging.getLogger(__name__).critical(msg, exc_info=sys.exc_info())
        status_code = 401
    except ValueError:
        msg = "Invalid message/option or invalid GCM response."
        logging.getLogger(__name__).critical(msg, exc_info=sys.exc_info())
        status_code = 400
    except Exception:
        msg = "DDCS server or GCM server internal error."
        logging.getLogger(__name__).critical(msg, exc_info=sys.exc_info())
        status_code = 500
    # retrying above four errors has little or no sense, so we don't do it
    # for now
    
    # we got the response, that's cool, now we can write the result
    pr = PushResult.objects.create(response_code=status_code)
    pr.save()
    sp.result = pr
    sp.save()

    if status_code != 200:
        return

    # update your registration ID's
    for reg_id, new_reg_id in results.canonical.items():
        policy.registration_id_changed(reg_id, new_reg_id)

    # probably app was uninstalled
    for reg_id in results.not_registered:
        policy.registration_id_revoked(reg_id)

    # unrecoverably failed, these ID's will not be retried
    for reg_id, _ in results.failed.items():
        policy.registration_id_revoked(reg_id)

    # if some registration ID's have recoverably failed
    if results.needs_retry():
        # construct new message with only failed regids
        if not policy.should_retry(sp, pr):
            return
        retry_msg = results.retry()
        data = retry_msg.__getstate__()['data']
        reg_ids = retry_msg.__getstate__()['registration_ids']
        reg_id = reg_ids[0]
        sec_offset = results.delay()
        send_at = datetime.datetime.utcnow().replace(tzinfo=utc) + datetime.timedelta(seconds=sec_offset)
        ScheduledPush.objects.create(
            policy,
            send_at=send_at,
            registration_id=reg_id,
            source=sp.source,
            data=data,
            attempt_no=sp.attempt_no+1,
        )
