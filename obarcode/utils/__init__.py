import frappe
from frappe import _
import datetime
import json
import random
import string
import urllib.request
import urllib.parse
import time
from frappe.core.doctype.user.user import STANDARD_USERS
from frappe.permissions import add_permission, update_permission_property
from frappe.utils.data import now_datetime
from frappe.utils.logger import set_log_level
from frappe.utils import cint, cstr, getdate
from frappe.utils import get_formatted_email


def get_attachment_path(dt, dn):
	return frappe.get_all("File","file_url",
		filters = {"attached_to_name": dn, "attached_to_doctype": dt})

def is_time_between(time_to_check, start_time, end_time):
    ''' Check Time is in between the give start and end time '''
    if time_to_check > start_time and time_to_check < end_time:
        return True
    return False

def formateTime(time_in_seconds):
    return datetime.datetime(2000, 1, 1) + datetime.timedelta(seconds = time_in_seconds)

def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def _now_ms(): return int(round(time.time() * 1000))

def get_date():
    _now = now_datetime()
    return '{}-{}-{}'.format(_now.year, _now.month, _now.day)

def send_mail(to, subject, template, add_args, now=False, retry =3,header_color = "green" ):
    """send mail"""
    from frappe.utils.user import get_user_fullname
    from frappe.utils import get_url

    created_by = get_user_fullname(frappe.session['user'])
    if created_by == "Guest" or created_by is None:
        created_by = "Administrator"

    args = {
        'title': subject,
        'site_url': get_url(),
        'created_by': created_by
    }

    args.update(add_args)

    sender = frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user) or None

    frappe.sendmail(recipients=to, sender=sender, subject=subject,
        template=template, args=args, header=[subject, header_color],
        delayed=now, retry=retry)