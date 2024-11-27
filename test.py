import requests


payload = {"year": 2024, "month": 11, "start": "", "end": ""}
headers = {"Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQyNDUwMjgsImlhdCI6MTczMTY1MzAyOCwicm9sZSI6InRlc3QiLCJzaWduIjoiYjY0Y2VlODMzOGRjZTc2ZjgxNjdmMDkyN2YwODYzZmMzYzkzOGE2OGYwOGM0NzI5NTBhNTQ5MmRmMzc1OGZjMCIsInN1YiI6IjgwNTUifQ.DHc24K1XWpDQk-sfiLiDhUDjau8AlOwaG4kg52R5XY4"}
response = requests.post(f"https://notify.eskiz.uz/api/message/export?status=all", data=payload, headers=headers)

print(response.text)