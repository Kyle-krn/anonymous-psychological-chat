import requests
import json
import time
from datetime import datetime, timedelta
from settings import QIWI_PRIVATE_KEY, QIWI_TOKEN, QIWI_NUMBER

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


def qiwi_balance():
    s = requests.Session()
    s.headers['Accept']= 'application/json'
    s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
    b = s.get(f'https://edge.qiwi.com/funding-sources/v2/persons/{QIWI_NUMBER}/accounts')
    data = b.json()
    rubAlias = [x for x in data['accounts'] if x['alias'] == 'qw_wallet_rub']
    rubBalance = rubAlias[0]['balance']['amount']
    return rubBalance


# Перевод на QIWI Кошелек
def send_p2p(to_qw, comment, sum_p2p):
    s = requests.Session()
    s.headers = {'content-type': 'application/json'}
    s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
    s.headers['User-Agent'] = 'Android v3.2.0 MKT'
    s.headers['Accept'] = 'application/json'
    
    postjson = {"id":"","sum":{"amount":"","currency":""},"paymentMethod":{"type":"Account","accountId":"643"}, "comment":"'+comment+'","fields":{"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = sum_p2p
    postjson['sum']['currency'] = '643'
    postjson['fields']['account'] = to_qw

    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments',json = postjson)
    print(res.json())
    return res.json()


