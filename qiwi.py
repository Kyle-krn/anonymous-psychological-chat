import requests
import json
from datetime import datetime, timedelta
from settings import QIWI_PRIVATE_KEY

headers = {
        'Authorization': f'Bearer {QIWI_PRIVATE_KEY}',
        "Content-Type": "application/json",
        "Accept": "application/json"
        }

def send_bill_api_qiwi(billid, coast, user_id):
    time_now = datetime.now().astimezone().replace(microsecond=0)
    time_bill = time_now + timedelta(hours=1)
    time_bill = time_bill.isoformat()
    

    params = {'amount': {'value': coast, 
                   'currency': 'RUB',
                   },
        'comment': f'User #{user_id} ---> {coast}',
        'expirationDateTime': time_bill, 
        'customer': {},
        'customFields': {},
        }
    
    params = json.dumps(params)

    url = f'https://api.qiwi.com/partner/bill/v1/bills/{billid}'
    
    res = requests.put(url,
                    headers=headers,
                    data=params,
                    )
    return (res.json(), time_now)

def reject_bill_api_qiwi(billid):
    params = {}
    url = f'https://api.qiwi.com/partner/bill/v1/bills/{billid}/reject'
    res = requests.post(url,
                        headers=headers,
                        data=params)
    
def check_bill_api_qiwi(billid):
    url = f'https://api.qiwi.com/partner/bill/v1/bills/{billid}'
    res = requests.get(url,headers=headers)
    return res.json()