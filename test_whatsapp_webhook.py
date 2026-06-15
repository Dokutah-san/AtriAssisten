import requests

payload = {
    'entry': [{
        'changes': [{
            'value': {
                'messages': [{
                    'from': '6281111111111',
                    'type': 'text',
                    'text': {'body': 'halo dari test'}
                }]
            }
        }]
    }]
}

for url in ['http://localhost:5005/webhook', 'https://chatty-grapes-grow.loca.lt/webhook']:
    try:
        r = requests.post(url, json=payload, timeout=30)
        print(url, r.status_code)
        print(r.text)
    except Exception as e:
        print(url, 'ERROR', e)
