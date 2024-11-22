from urllib.request import urlopen
import json
import pandas as pd
import time

#Downloading meeting (weekend) list of year 2023
print('Accessing meeting list...')
response = urlopen('https://api.openf1.org/v1/meetings?year=2023')
mtg_data = json.loads(response.read().decode('utf-8'))
mtg_df = pd.DataFrame(mtg_data)

time.sleep(1)

session_df = pd.DataFrame()
position_df = pd.DataFrame()
session_list = []
for meetings in mtg_data:
    print(f'fetching {meetings['meeting_name']} session data...')
    response = urlopen(f"https://api.openf1.org/v1/sessions?meeting_key={meetings['meeting_key']}")
    session_data = json.loads(response.read().decode('utf-8'))
    session_actual = pd.DataFrame(session_data)
    session_df = pd.concat([session_df, session_actual], ignore_index=True)
    for session in session_data:
        print(f'    {session['session_key']} position details...')
        position_details = urlopen(f"https://api.openf1.org/v1/position?session_key={session['session_key']}")
        position_data = json.loads(position_details.read().decode('utf-8'))
        #print(position_data)
        position_actual = pd.DataFrame(position_data)
        position_df = pd.concat([position_df, position_actual], ignore_index=True)
        time.sleep(0.2)

time.sleep(1)

weather_df = pd.DataFrame()
for meetings in mtg_data:
    print(f'fetching {meetings['meeting_name']} weather data...')
    response = urlopen(f"https://api.openf1.org/v1/weather?meeting_key={meetings['meeting_key']}")
    weather_data = json.loads(response.read().decode('utf-8'))
    weather_actual = pd.DataFrame(weather_data)
    weather_df = pd.concat([weather_df, weather_actual], ignore_index=True)





print(">mtg")
print(mtg_df)
print(">session")
print(session_df)
print(">position")
print(position_df)
print(">weather")
print(weather_df)

