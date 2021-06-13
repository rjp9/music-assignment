import requests
import json

for i in range(100):
    r = requests.request('POST', 
        'http://127.0.0.1:5000/api/assignment', 
        data=json.dumps({
            'email': f'{i}',
            'option': 'first'
        }), 
        headers={'content-type': 'application/json'}
    )
    # if i == 0:
    #     print(r.text)

