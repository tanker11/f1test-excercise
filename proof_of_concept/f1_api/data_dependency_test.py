from urllib.request import urlopen
import json
import pandas as pd

#Downloading meeting (race) list od year 2023
response = urlopen('https://api.openf1.org/v1/meetings?year=2023')
mtg_data = json.loads(response.read().decode('utf-8'))
print(mtg_data)

race_sessions = []
#Iterating through all races
for meetings in mtg_data:
    print("*" * 40)
    print(f'fetching {meetings['meeting_name']} meeting data...')
    response = urlopen(f"https://api.openf1.org/v1/sessions?meeting_key={meetings['meeting_key']}")
    session_data = json.loads(response.read().decode('utf-8'))
    for session in session_data:
        print(session['session_type'],session['session_name'],session['session_key'])
        if session['session_name']=='Race':
            race_sessions.append(session['session_key'])
print(race_sessions)







