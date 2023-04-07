from .smsby import SMSBY
from .senders_config import API_KEY


sms = SMSBY(API_KEY, 'by')


def send_results_sms(message, phone):
    response = sms.send_quick_sms(message, phone)
    return response
