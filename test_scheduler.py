"""
Phase 2 tests — qualification filtering.
Run with: python test_scheduler.py
If nothing prints an error and you see "All Phase 2 tests passed", it works.
"""

import data
import scheduler

# Job 101 needs HVAC. Only Adam, Chris, Dana have it.
result = scheduler.filter_by_qualification(data.jobs[0], data.technicians)
names = [t["name"] for t in result]

assert names == ["Adam", "Chris", "Dana"], f"Expected Adam/Chris/Dana, got {names}"

# A technician with the wrong skill must be excluded.
assert "Ben" not in names, "Ben has no HVAC skill and should be excluded"

print("All Phase 2 tests passed")