"""P3 Scheduling System — fictional seed data""

These records stand in for a database (that arrives in Phase 6).
Technicians are EXISTING company staff. Jobs are what the manager wants to assign.
Times are real `time` objects so they compare correctly.
"""
from datetime import time

# --- Technicians: five existing staff members ---
# Each is a dictionary. `skills` and `bookings` are lists.
technicians = [
    {
        "id": 1,
        "name": "Adam",
        "skills": ["HVAC"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Hoppers Crossing",
        "available": True,
        "bookings": [],        # no jobs assigned yet
    },
    {
        "id": 2,
        "name": "Ben",
        "skills": ["Electrical"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Tarneit",
        "available": True,
        "bookings": [],
    },
    {
        "id": 3,
        "name": "Chris",
        "skills": ["HVAC", "Electrical"],
        "shift_start": time(8, 0),
        "shift_end": time(16, 0),
        "service_area": "Werribee",
        "available": True,
        "bookings": [],
    },
    {
        "id": 4,
        "name": "Dana",
        "skills": ["HVAC"],
        "shift_start": time(10, 0),
        "shift_end": time(18, 0),
        "service_area": "Point Cook",
        "available": True,
        "bookings": [],
    },
    {
        "id": 5,
        "name": "Erin",
        "skills": ["Plumbing"],
        "shift_start": time(9, 0),
        "shift_end": time(17, 0),
        "service_area": "Tarneit",
        "available": False,     # currently unavailable
        "bookings": [],
    },
]

# --- Jobs: a couple of examples to test against ---
jobs = [
    {
        "id": 101,
        "job_type": "Air-conditioner repair",
        "required_skill": "HVAC",
        "suburb": "Hoppers Crossing",
        "start": time(11, 0),
        "end": time(13, 0),       # 2-hour job
    },
    {
        "id": 102,
        "job_type": "Heating repair",
        "required_skill": "HVAC",
        "suburb": "Werribee",
        "start": time(14, 0),
        "end": time(15, 30),      # 1.5-hour job
    },
]
