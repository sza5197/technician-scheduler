"""
Phase 2 tests — qualification filtering.
Run with: python test_scheduler.py
If nothing prints an error and you see "All Phase 2 tests passed", it works.
"""

import data
import scheduler
from datetime import time

# Job 101 needs HVAC. Only Adam, Chris, Dana have it.
result = scheduler.filter_by_qualification(data.jobs[0], data.technicians)
names = [t["name"] for t in result]

assert names == ["Adam", "Chris", "Dana"], f"Expected Adam/Chris/Dana, got {names}"

# A technician with the wrong skill must be excluded.
assert "Ben" not in names, "Ben has no HVAC skill and should be excluded"

print("All Phase 2 tests passed")


# Clash: 10:00-12:00 vs 11:00-13:00 share the 11-12 hour.
assert scheduler.overlaps(time(10, 0), time(12, 0), time(11, 0), time(13, 0)) == True, \
    "10-12 and 11-13 should clash"

# No clash: 9:00-11:00 vs 11:00-13:00 only touch at 11:00.
assert scheduler.overlaps(time(9, 0), time(11, 0), time(11, 0), time(13, 0)) == False, \
    "9-11 and 11-13 only touch, should NOT clash"

# No clash: completely separate times.
assert scheduler.overlaps(time(9, 0), time(10, 0), time(14, 0), time(15, 0)) == False, \
    "9-10 and 14-15 are far apart, should NOT clash"

print("All Phase 3 tests passed")

# --- Phase 4: full eligibility ---
import copy
techs = copy.deepcopy(data.technicians)
for t in techs:
    if t["name"] == "Chris":
        t["bookings"].append({"start": time(10, 0), "end": time(12, 0)})

eligible, rejected = scheduler.find_eligible_technicians(data.jobs[0], techs)
eligible_names = [t["name"] for t in eligible]
reasons = {r["name"]: r["reason"] for r in rejected}

assert "Adam" in eligible_names, "Adam should be eligible"
assert "Dana" in eligible_names, "Dana should be eligible"
assert "Chris" not in eligible_names, "Chris clashes 10-12 with the 11-13 job"
assert "unavailable" in reasons["Erin"], "Erin should be rejected as unavailable"
assert "skill" in reasons["Ben"], "Ben should be rejected for missing skill"
assert "booked" in reasons["Chris"], "Chris should be rejected for a booking clash"

print("All Phase 4 tests passed")

# --- Phase 5: recommendation ---

# Give Adam two bookings so Dana (zero bookings) has the lighter workload.
techs2 = copy.deepcopy(data.technicians)
for t in techs2:
    if t["name"] == "Adam":
        t["bookings"].append({"start": time(9, 0), "end": time(10, 0)})
        t["bookings"].append({"start": time(14, 0), "end": time(15, 0)})

# Job 101: HVAC, 11:00-13:00. Both Adam and Dana are eligible; Dana is lighter.
recommended, eligible, rejected = scheduler.recommend_technician(data.jobs[0], techs2)
# Adam now has 2 bookings. Chris and Dana are tied at 0, so the id tie-break
# picks Chris (id 3) over Dana (id 4). This proves the deterministic tie-break works.
assert recommended["name"] == "Chris", f"Chris wins the 0-workload tie by id, got {recommended['name']}"

# No-eligible case: a job needing a skill nobody available has.
impossible_job = {"id": 999, "job_type": "Gas fitting", "required_skill": "GasFitting",
                  "suburb": "Tarneit", "start": time(11, 0), "end": time(12, 0)}
rec2, elig2, rej2 = scheduler.recommend_technician(impossible_job, data.technicians)
assert rec2 is None, "Nobody has GasFitting, recommendation should be None"
assert len(elig2) == 0, "No one should be eligible for the impossible job"

print("All Phase 5 tests passed")