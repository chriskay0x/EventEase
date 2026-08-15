import requests
from django.conf import settings

def _headers():
    return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"}

def verify_transaction(reference):
    r = requests.get(f"{settings.PAYSTACK_API}/transaction/verify/{reference}", headers=_headers(), timeout=15)
    r.raise_for_status(); return r.json()

def create_recipient(name, account_number, bank_code):
    r = requests.post(f"{settings.PAYSTACK_API}/transfer/recipient", headers=_headers(),
                      json={"type": "nuban", "name": name, "account_number": account_number,
                            "bank_code": bank_code, "currency": settings.PAYSTACK_CURRENCY}, timeout=15)
    r.raise_for_status(); return r.json()

def transfer(recipient_code, amount_kobo, reason):
    r = requests.post(f"{settings.PAYSTACK_API}/transfer", headers=_headers(),
                      json={"recipient": recipient_code, "amount": amount_kobo, "reason": reason}, timeout=15)
    r.raise_for_status(); return r.json()