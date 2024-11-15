import requests

url = "https://notify.eskiz.uz/api/message/sms/get-user-messages"

payload={'start_date': '2024-11-01 00:00',
'end_date': '2024-11-15 23:59',
'page_size': '20',
'count': '0'}
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQyNDUwMjgsImlhdCI6MTczMTY1MzAyOCwicm9sZSI6InRlc3QiLCJzaWduIjoiYjY0Y2VlODMzOGRjZTc2ZjgxNjdmMDkyN2YwODYzZmMzYzkzOGE2OGYwOGM0NzI5NTBhNTQ5MmRmMzc1OGZjMCIsInN1YiI6IjgwNTUifQ.DHc24K1XWpDQk-sfiLiDhUDjau8AlOwaG4kg52R5XY4'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
