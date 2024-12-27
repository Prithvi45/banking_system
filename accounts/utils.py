from django.core.mail import send_mail
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import requests
from decimal import Decimal

EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/"

def send_otp_via_email(email, otp):
    print("reached here")
    print(settings.SENDGRID_API_KEY)
    """
    Send an email using SendGrid.
    """
    try:
        subject = "Your OTP for Login"
        message = f"Your One-Time Password (OTP) is: {otp}. It will expire in 30 minutes."        
        message = Mail(
            from_email="prithvimane45@gmail.com",
            to_emails=email,
            subject=subject,
            html_content=message
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(response)
        return response.status_code, response.body, response.headers
    except Exception as e:
        print(str(e))
        return str(e)


def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another using ExchangeRatesAPI."""
    if from_currency == to_currency:
        return Decimal(amount)  # No conversion needed

    try:
        response = requests.get(f"{EXCHANGE_RATE_API}{from_currency}")
        response.raise_for_status()
        rates = response.json().get('rates', {})
        conversion_rate = rates.get(to_currency)

        if conversion_rate:
            # Apply a 0.01 spread
            conversion_rate = Decimal(conversion_rate) * Decimal('1.01')
            return Decimal(amount) * conversion_rate
        else:
            raise ValueError("Currency conversion rate not available.")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching conversion rates: {e}")



'''
def send_otp_via_email(email, otp):
    subject = "Your OTP for Login"
    message = f"Your One-Time Password (OTP) is: {otp}. It will expire in 5 minutes."
    from_email = "noreply@yourdomain.com"
    send_mail(subject, message, from_email, [email])
'''    
