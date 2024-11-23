SELECT m.location, s.session_name, p.driver_number
FROM meetings m
JOIN sessions s
ON s.meeting_key=m.meeting_key
JOIN positions p
ON p.session_key=s.session_key