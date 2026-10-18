#P3 Scheduling System — scheduling logic--------------------Phases 2-4: qualification, time overlap, and full eligibility checks.

def has_required_skill(technician, job):
    """Return True if the technician has the skill the job requires."""
    return job["required_skill"] in technician["skills"]


def filter_by_qualification(job, technicians):
    """Return only the technicians who have the job's required skill."""
    eligible = []
    for technician in technicians:
        if has_required_skill(technician, job):
            eligible.append(technician)
    return eligible


def overlaps(start_a, end_a, start_b, end_b):
    """
    Return True if two time ranges clash.
    Ranges that only touch at an endpoint (9-11 and 11-13) do NOT clash.
    """
    return start_a < end_b and start_b < end_a


def find_eligible_technicians(job, technicians):
    """
    Check all hard constraints for each technician.
    Returns (eligible, rejected):
      eligible -> technicians who pass every constraint
      rejected -> {"name", "reason"} for each technician who fails
    """
    eligible = []
    rejected = []

    for technician in technicians:
        # 1. Availability
        if not technician["available"]:
            rejected.append({"name": technician["name"],
                             "reason": "marked unavailable"})
            continue

        # 2. Skill
        if not has_required_skill(technician, job):
            rejected.append({"name": technician["name"],
                             "reason": f"lacks required skill ({job['required_skill']})"})
            continue

        # 3. Job must fit inside the shift
        if job["start"] < technician["shift_start"] or job["end"] > technician["shift_end"]:
            rejected.append({"name": technician["name"],
                             "reason": "job falls outside working hours"})
            continue

        # 4. Job must not clash with an existing booking
        has_conflict = False
        for booking in technician["bookings"]:
            if overlaps(job["start"], job["end"], booking["start"], booking["end"]):
                has_conflict = True
                break
        if has_conflict:
            rejected.append({"name": technician["name"],
                             "reason": "already booked at that time"})
            continue

        eligible.append(technician)

    return eligible, rejected

def workload(technician):
    """Count how many bookings a technician already has. Fewer = preferred."""
    return len(technician["bookings"])


def recommend_technician(job, technicians):
    """
    Decide who SHOULD take the job, among those who CAN.

    Returns (recommended, eligible, rejected):
      recommended -> the chosen technician dict, or None if nobody is eligible
      eligible    -> all technicians who passed the hard constraints
      rejected    -> {"name", "reason"} for those who failed
    """
    eligible, rejected = find_eligible_technicians(job, technicians)

    if not eligible:
        return None, eligible, rejected

    # Sort by workload (fewest first), then by id as a predictable tie-breaker.
    eligible_sorted = sorted(eligible, key=lambda t: (workload(t), t["id"]))
    recommended = eligible_sorted[0]
    return recommended, eligible_sorted, rejected


def build_explanation(job, recommended, eligible, rejected):
    """Build a plain-English explanation that reflects the real checks."""
    lines = []

    if recommended is None:
        lines.append(f"No technician can take '{job['job_type']}' "
                     f"({job['start'].strftime('%H:%M')}-{job['end'].strftime('%H:%M')}).")
    else:
        lines.append(f"{recommended['name']} is recommended: has the required "
                     f"{job['required_skill']} skill, is available for the full booking, "
                     f"and has the lightest workload ({workload(recommended)} existing jobs).")

    for r in rejected:
        lines.append(f"{r['name']} was not eligible — {r['reason']}.")

    return "\n".join(lines)