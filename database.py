"""
P3 Scheduling System — database setup (SQLite).
Sub-step 1: create the technicians and skills tables.
"""

import sqlite3
from datetime import datetime


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

if __name__ == "__main__":
    create_tables()
    seed_technicians()