"""
IT Help Desk Scheduler — seed data.

These records stand in for a database (created in the database layer).
Support agents are EXISTING staff. Tickets are what the manager wants to assign.
Times are real `time` objects so they compare correctly.
"""

from datetime import time

# --- Support agents: five existing staff members ---
technicians = [
    {
        "id": 1,
        "name": "Adam",
        "skills": ["Network"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Finance",
        "available": True,
        "bookings": [],
    },
    {
        "id": 2,
        "name": "Ben",
        "skills": ["Accounts"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Sales",
        "available": True,
        "bookings": [],
    },
    {
        "id": 3,
        "name": "Chris",
        "skills": ["Network", "Software"],
        "shift_start": time(8, 0),
        "shift_end": time(16, 0),
        "service_area": "HR",
        "available": True,
        "bookings": [],
    },
    {
        "id": 4,
        "name": "Dana",
        "skills": ["Network"],
        "shift_start": time(10, 0),
        "shift_end": time(18, 0),
        "service_area": "Operations",
        "available": True,
        "bookings": [],
    },
    {
        "id": 5,
        "name": "Erin",
        "skills": ["Hardware"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Sales",
        "available": False,     # currently unavailable
        "bookings": [],
    },
]

# --- Tickets: a couple of examples to test against ---
jobs = [
    {
        "id": 101,
        "job_type": "WiFi not connecting",
        "required_skill": "Network",
        "suburb": "Finance",
        "start": time(11, 0),
        "end": time(13, 0),       # 2-hour ticket
    },
    {
        "id": 102,
        "job_type": "Software install request",
        "required_skill": "Software",
        "suburb": "HR",
        "start": time(14, 0),
        "end": time(15, 30),      # 1.5-hour ticket
    },
]