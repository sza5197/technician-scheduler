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