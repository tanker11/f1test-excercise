from urllib.request import urlopen
import json

response = urlopen('https://api.openf1.org/v1/meetings?year=2023')
data = json.loads(response.read().decode('utf-8'))
for meeting in data:
    print(meeting['meeting_name'])

