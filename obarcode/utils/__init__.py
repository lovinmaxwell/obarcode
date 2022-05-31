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


@frappe.whitelist()
def generate_item_barcode(dt,dn,item_name,item_rate,item_barcode,qty=1,x=50,y=25):
    """
		Generate Item Barcode
    """
    import os
    from PyPDF2 import PdfFileReader,PdfFileMerger
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.graphics.barcode import eanbc
    from reportlab.graphics.shapes import Drawing 
    from erpnext import get_default_company
    from obarcode.utils import _now_ms,random_string
    from frappe.utils.file_manager import save_file
    
    merger = PdfFileMerger()

    xLabel = float(x)*mm
    yLabel = float(y)*mm
    fileName = f'{_now_ms()}.pdf'
    for i in range(int(qty)):
        # creating a pdf object
        pdf = canvas.Canvas(fileName,pagesize=(xLabel,yLabel))
        string = item_barcode
        pdf.setFillColorRGB(0,0,0) # change colors of text here
        pdf.setFont("Courier-Bold", 8)
        #   from reportlab.graphics.barcode import eanbc,code39,code128
        # 	barcode = code39.Extended39(string) # code39 type barcode generation here
        # 	barcode = code128.Code128(string, humanReadable=True)
        # 	barcode.drawOn(pdf, x_var*mm , y_var*mm) # coordinates for barcode?
        barcode_eanbc13 = eanbc.Ean13BarcodeWidget(string,barHeight=yLabel/2)
        d = Drawing(xLabel,20*mm)
        d.add(barcode_eanbc13)
        # d.drawOn(pdf, xLabel*0.20, yLabel*0.20)
        d.drawOn(pdf, xLabel*0.20 if int(x) == 50 else xLabel*0.05, yLabel*0.25)
        company_name = get_default_company()
        pdf.drawCentredString(xLabel/2, yLabel*0.85, company_name)
        pdf.drawCentredString(xLabel/2, yLabel*0.10, item_name)
        pdf.rotate(90)
        pdf.drawCentredString(yLabel/2, -xLabel*0.10, item_rate)
        pdf.save()
        f1 = PdfFileReader(open(fileName, 'rb'))
        merger.append(f1)

    mFileName = f'{_now_ms()}.pdf'
    merger.write(mFileName)

    f1 = open(mFileName, 'rb')
    to_name = random_string(random.randint(1,6),"1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ").zfill(6)
    file_name = "{}-{}.pdf".format(item_barcode,to_name.replace(" ", "-").replace("/", "-"))
    save_file(file_name, f1.read(), dt,dn , is_private=1)
    if os.path.exists(fileName):os.remove(fileName)
    if os.path.exists(mFileName):os.remove(mFileName)