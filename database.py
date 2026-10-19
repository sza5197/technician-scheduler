"""
P3 Scheduling System — database setup (SQLite).
Sub-step 1: create the technicians and skills tables.
"""

import sqlite3
from datetime import datetime
import scheduler


DB_NAME = "scheduler.db"   # the database file that will appear in your folder


def get_connection():
    """Open a connection to the database file."""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create the technicians and skills tables if they don't already exist."""
    connection = get_connection()
    cursor = connection.cursor()

    # The people. No skills column here — skills live in their own table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technicians (
            id            INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            shift_start   TEXT NOT NULL,
            shift_end     TEXT NOT NULL,
            service_area  TEXT,
            available     INTEGER NOT NULL
        )
    """)

    # One row per technician-skill pair. technician_id points back to technicians.id.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id             INTEGER PRIMARY KEY,
            technician_id  INTEGER NOT NULL,
            skill          TEXT NOT NULL,
            FOREIGN KEY (technician_id) REFERENCES technicians(id)
        )
    """)

    # Jobs the manager creates.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id              INTEGER PRIMARY KEY,
            job_type        TEXT NOT NULL,
            required_skill  TEXT NOT NULL,
            suburb          TEXT,
            start_time      TEXT NOT NULL,
            end_time        TEXT NOT NULL
        )
    """)

    # Confirmed bookings: links a job to the technician doing it.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id             INTEGER PRIMARY KEY,
            job_id         INTEGER NOT NULL,
            technician_id  INTEGER NOT NULL,
            FOREIGN KEY (job_id) REFERENCES jobs(id),
            FOREIGN KEY (technician_id) REFERENCES technicians(id)
        )
    """)
    
    connection.commit()   # save the changes
    connection.close()    # close the connection
    print("Tables created (or already exist).")


import data   # our seed technicians


def seed_technicians():
    """Load the five technicians from data.py into the database tables."""
    connection = get_connection()
    cursor = connection.cursor()

    for technician in data.technicians:
        # Insert the person into the technicians table.
        # Times are stored as text like "09:00". available True/False -> 1/0.
        cursor.execute("""
            INSERT INTO technicians (name, shift_start, shift_end, service_area, available)
            VALUES (?, ?, ?, ?, ?)
        """, (
            technician["name"],
            technician["shift_start"].strftime("%H:%M"),
            technician["shift_end"].strftime("%H:%M"),
            technician["service_area"],
            1 if technician["available"] else 0,
        ))

        # The id SQLite just assigned to this technician.
        new_id = cursor.lastrowid

        # Insert each of this technician's skills as its own row,
        # linking it back with technician_id = new_id.  <-- the foreign key in action
        for skill in technician["skills"]:
            cursor.execute(
                "INSERT INTO skills (technician_id, skill) VALUES (?, ?)",
                (new_id, skill),
            )

    connection.commit()
    connection.close()
    print(f"Seeded {len(data.technicians)} technicians.")



def text_to_time(text):
    """Convert stored text like '09:00' back into a real time object."""
    return datetime.strptime(text, "%H:%M").time()


def load_technicians():
    """
    Read all technicians WITH their skills from the database,
    returned as the same dictionaries the scheduler already uses.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Get the technicians first.
    cursor.execute("""
        SELECT id, name, shift_start, shift_end, service_area, available
        FROM technicians
    """)
    rows = cursor.fetchall()

    technicians = []
    for row in rows:
        tech_id, name, shift_start, shift_end, service_area, available = row

        # Get THIS technician's skills (a separate small query per technician).
        cursor.execute(
            "SELECT skill FROM skills WHERE technician_id = ?",
            (tech_id,),
        )
        skill_rows = cursor.fetchall()
        skills = [s[0] for s in skill_rows]   # unwrap each (skill,) tuple into a plain list

        technicians.append({
            "id": tech_id,
            "name": name,
            "skills": skills,
            "shift_start": text_to_time(shift_start),
            "shift_end": text_to_time(shift_end),
            "service_area": service_area,
            "available": bool(available),      # 1 -> True, 0 -> False
            "bookings": [],                    # filled from the assignments table in Sub-step 4
        })

    connection.close()
    return technicians


def save_job(job):
    """Insert a job into the jobs table. Returns the new job's id."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO jobs (job_type, required_skill, suburb, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        job["job_type"],
        job["required_skill"],
        job["suburb"],
        job["start"].strftime("%H:%M"),
        job["end"].strftime("%H:%M"),
    ))
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return new_id


def load_technicians_with_bookings():
    """
    Load technicians (with skills), AND fill each one's bookings list
    from the assignments table, so conflict checks see saved bookings.
    """
    technicians = load_technicians()   # reuse what we built in sub-step 3

    connection = get_connection()
    cursor = connection.cursor()

    for tech in technicians:
        # Find every job assigned to this technician, with that job's times.
        cursor.execute("""
            SELECT jobs.start_time, jobs.end_time
            FROM assignments
            JOIN jobs ON jobs.id = assignments.job_id
            WHERE assignments.technician_id = ?
        """, (tech["id"],))
        for start_text, end_text in cursor.fetchall():
            tech["bookings"].append({
                "start": text_to_time(start_text),
                "end": text_to_time(end_text),
            })

    connection.close()
    return technicians


def confirm_assignment(job, technician_id):
    """
    Save a booking ONLY if the technician is still eligible right now.
    Returns True if saved, False if the technician is no longer valid.
    """
    # Re-check eligibility against the CURRENT saved bookings.
    technicians = load_technicians_with_bookings()
    eligible, rejected = scheduler.find_eligible_technicians(job, technicians)
    eligible_ids = [t["id"] for t in eligible]

    if technician_id not in eligible_ids:
        return False   # someone/something changed — refuse to save an invalid booking

    # Still valid -> save the assignment.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO assignments (job_id, technician_id) VALUES (?, ?)",
        (job["id"], technician_id),
    )
    connection.commit()
    connection.close()
    return True

import scheduler   # we reuse the eligibility check at confirm time


def save_job(job):
    """Insert a job into the jobs table. Returns the new job's id."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO jobs (job_type, required_skill, suburb, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    """, (
        job["job_type"],
        job["required_skill"],
        job["suburb"],
        job["start"].strftime("%H:%M"),
        job["end"].strftime("%H:%M"),
    ))
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()
    return new_id


def load_technicians_with_bookings():
    """
    Load technicians (with skills), AND fill each one's bookings list
    from the assignments table, so conflict checks see saved bookings.
    """
    technicians = load_technicians()   # reuse what we built in sub-step 3

    connection = get_connection()
    cursor = connection.cursor()

    for tech in technicians:
        # Find every job assigned to this technician, with that job's times.
        cursor.execute("""
            SELECT jobs.start_time, jobs.end_time
            FROM assignments
            JOIN jobs ON jobs.id = assignments.job_id
            WHERE assignments.technician_id = ?
        """, (tech["id"],))
        for start_text, end_text in cursor.fetchall():
            tech["bookings"].append({
                "start": text_to_time(start_text),
                "end": text_to_time(end_text),
            })

    connection.close()
    return technicians


def confirm_assignment(job, technician_id):
    """
    Save a booking ONLY if the technician is still eligible right now.
    Returns True if saved, False if the technician is no longer valid.
    """
    # Re-check eligibility against the CURRENT saved bookings.
    technicians = load_technicians_with_bookings()
    eligible, rejected = scheduler.find_eligible_technicians(job, technicians)
    eligible_ids = [t["id"] for t in eligible]

    if technician_id not in eligible_ids:
        return False   # someone/something changed — refuse to save an invalid booking

    # Still valid -> save the assignment.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO assignments (job_id, technician_id) VALUES (?, ?)",
        (job["id"], technician_id),
    )
    connection.commit()
    connection.close()
    return True

def load_jobs():
    """Read all jobs from the database as dictionaries the scheduler can use."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, job_type, required_skill, suburb, start_time, end_time
        FROM jobs
    """)
    jobs = []
    for row in cursor.fetchall():
        job_id, job_type, required_skill, suburb, start_text, end_text = row
        jobs.append({
            "id": job_id,
            "job_type": job_type,
            "required_skill": required_skill,
            "suburb": suburb,
            "start": text_to_time(start_text),
            "end": text_to_time(end_text),
        })
    connection.close()
    return jobs


def load_job(job_id):
    """Load one job by its id. Returns the job dict, or None if not found."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, job_type, required_skill, suburb, start_time, end_time
        FROM jobs WHERE id = ?
    """, (job_id,))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    job_id, job_type, required_skill, suburb, start_text, end_text = row
    return {
        "id": job_id,
        "job_type": job_type,
        "required_skill": required_skill,
        "suburb": suburb,
        "start": text_to_time(start_text),
        "end": text_to_time(end_text),
    }


if __name__ == "__main__":
    create_tables()
    seed_technicians()