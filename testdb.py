import requests
import json
import random
import time

# URL = 'http://127.0.0.1:5000/api/assignment'
URL = 'http://mind.cs.byu.edu:3000/api/assignment'
for i in range(10):
    for i in range(25):
        time.sleep(random.randint(1, 5))
        email = str(i)
        option = random.choice(['first', 'returning'])
        r = requests.request('POST', 
            URL, 
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


