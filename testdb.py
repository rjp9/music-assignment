import requests
import json
import random


for i in range(10):
    for i in range(25):
        email = str(i)
        option = random.choice(['first', 'returning'])
        r = requests.request('POST', 
            'http://127.0.0.1:5000/api/assignment', 
            data=json.dumps({
                'email': email,
                'option': option
            }), 
            headers={'content-type': 'application/json'}
        )
        if 'application/pdf' in r.headers['content-type']:
            print(f'email {email}: pdf')
        else:
            print(f'email {email}: {r.text}')


