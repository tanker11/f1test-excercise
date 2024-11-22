select location, s.session_name, p.driver_number
from meetings m
join sessions s
on s.meeting_key=m.meeting_key
join positions p
on p.session_key=s.session_key