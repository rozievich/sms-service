# import requests
# from uuid import uuid4

# url = "https://notify.eskiz.uz/api/message/sms/send-batch"

# payload = {
#     "messages": [
#         {"user_sms_id": str(uuid4()),"to": 998333305378, "text": "Это тест от Eskiz"},
#         {"user_sms_id": str(uuid4()),"to": 998912141787, "text": "Это тест от Eskiz"},
#         {"user_sms_id": str(uuid4()),"to": 998940344454, "text": "Это тест от Eskiz"}
#     ],
#     "from": "4546",
#     "dispatch_id": str(uuid4()),
# }

# headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQwODk4NTgsImlhdCI6MTczMTQ5Nzg1OCwicm9sZSI6InRlc3QiLCJzaWduIjoiYjY0Y2VlODMzOGRjZTc2ZjgxNjdmMDkyN2YwODYzZmMzYzkzOGE2OGYwOGM0NzI5NTBhNTQ5MmRmMzc1OGZjMCIsInN1YiI6IjgwNTUifQ.pUDW6y1pjPMUIuHHQaethFBI7Q9YNLZ_NWB4K0H68BE'}

# response = requests.post(url, headers=headers, json=payload)

# print(response.json())

import requests

url = "https://notify.eskiz.uz/api/message/sms/send-batch"

payload = "{\r\n    \"messages\": [\r\n        {\"user_sms_id\":\"sms1\",\"to\": 998990000000, \"text\": \"eto test\"},\r\n        {\"user_sms_id\":\"sms2\",\"to\": 998980000000, \"text\": \"eto test 2\"}\r\n    ],\r\n    \"from\": \"4546\",\r\n    \"dispatch_id\": 123\r\n}"
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQwODk4NTgsImlhdCI6MTczMTQ5Nzg1OCwicm9sZSI6InRlc3QiLCJzaWduIjoiYjY0Y2VlODMzOGRjZTc2ZjgxNjdmMDkyN2YwODYzZmMzYzkzOGE2OGYwOGM0NzI5NTBhNTQ5MmRmMzc1OGZjMCIsInN1YiI6IjgwNTUifQ.pUDW6y1pjPMUIuHHQaethFBI7Q9YNLZ_NWB4K0H68BE'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
