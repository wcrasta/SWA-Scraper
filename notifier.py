import configparser
from datetime import datetime
from twilio.rest import TwilioRestClient

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
ACCOUNT_SID = CONFIG['twilio']['account_sid']
AUTH_TOKEN = CONFIG['twilio']['auth_token']
FROM_NUMBER = CONFIG['twilio']['from_number']
TO_NUMBER = CONFIG['twilio']['to_number']

def sendNotification(real_total, max_price):
    """
    Sends an SMS message using Twilio.
    """
    print("[%s] Found a deal. Max Total: %s. Current Total: %s." % (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        max_price, str(real_total)))

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        body="[%s] Found a deal. Max Total: %s. Current Total: %s" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            max_price,
            str(real_total)))

    print("[%s] Text message sent!" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
