"""
P3 Scheduling System — scheduling logic.
Phase 2: filter technicians by whether they have the required skill.
"""


def has_required_skill(technician, job):
    """
    Return True if this technician has the skill the job requires.

    `technician` is one technician dictionary.
    `job` is one job dictionary.
    We check whether job's required_skill is in the technician's skills list.
    """
    return job["required_skill"] in technician["skills"]


def filter_by_qualification(job, technicians):
    """
    Return a new list containing only technicians who have the skill this job requires
    """
    eligible = []
    for technician in technicians:
        if has_required_skill(technician, job):
            eligible.append(technician)
    return eligible

