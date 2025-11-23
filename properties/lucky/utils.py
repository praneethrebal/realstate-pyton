# listings/utils.py
from twilio.rest import Client
import os

TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH = os.environ.get("TWILIO_AUTH")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")  # e.g. "whatsapp:+1415XXXXXXX"
ADMIN_WHATSAPP = "whatsapp:+916300297048"  # the number you specified, with country code

def send_whatsapp_verification_message(purchase):
    if not TWILIO_SID or not TWILIO_AUTH:
        return
    client = Client(TWILIO_SID, TWILIO_AUTH)
    body = (f"Purchase Verified!\nProperty: {purchase.property.luck_id}\n"
            f"Buyer: {purchase.buyer.full_name} ({purchase.buyer.whatsapp_no})\n"
            f"Tickets: {purchase.quantity}\nTicket Codes: {purchase.ticket_codes}\n")
    # send to admin
    client.messages.create(body=body, from_=TWILIO_WHATSAPP_FROM, to=ADMIN_WHATSAPP)
    # send to buyer if they provided whatsapp_no
    if purchase.buyer.whatsapp_no:
        buyer_to = "whatsapp:" + purchase.buyer.whatsapp_no
        client.messages.create(body=f"Your purchase for {purchase.property.luck_id} is VERIFIED.\nTickets: {purchase.ticket_codes}", from_=TWILIO_WHATSAPP_FROM, to=buyer_to)
