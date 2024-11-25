SELECT m.location, s.session_name, m.meeting_key, s.session_key, p.driver_number, p.position, p.date,
    DENSE_RANK() OVER(ORDER BY p.date ASC) AS LapNo
FROM meetings m
JOIN sessions s
ON s.meeting_key=m.meeting_key
JOIN positions p
ON p.session_key=s.session_key
WHERE s.session_name='Race' AND m.location='Melbourne'