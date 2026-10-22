Technician Scheduler
---------------------
A small internal web tool that helps a manager assign repair jobs to the right technician.

THE PROBLEM
-----------
Say a heating/cooling company has several technicians and incoming repair jobs, deciding who takes which job isn't obvious as some technicians may not be qualified for the job, or some may already be booked. Allocating by hand is slow and easy to get wrong.
Given a job and the current technicians, this tool filters out everyone who can't do it and reccomends the best of who's left.

This project applies not only to heating/cooling companies, but can be twisted and molded into companies of different nature; examples are below:
1) Delivery company - Drivers could be allocated to deliveries (skills = license, vehicle type)
2) Medical clinic - Patient appointments (skill = specialty, working hours, etc..)
3) IT/Software support - Engineers allocated to support tickets (skill = area of expertise such as networking/databses)
4) Venues/Facilities - rooms or equipment organised in relation to a booking (Room type/facilities included)
5) Trades (current) - Carpenting/Automotive/Plumbing/electrical/AC repair. 

NOTE: The current project takes into account a generalised 'Trades' comapany, one which oversees more than one type (includes electrical/pumbing/HVAC, uses these 3 as the 'skills').

HOW IT WORKS
------------
Each technician is checked against 4 hard rules; they must pass all to be eligible for the current job.
1) Skill - has the qualificaation the job needs
2) Availability - isn't marked unavailable (off sick/on leave)
3) Working hours - the job fits inside their designated work hours
4) No Clash - The job doesent overlap a booking they already have.

Amonst those who pass, it ranks the list of available technicians by workload (to spread work fairly), if the workload remains the same, the tiebreaker is sorted by taking into the account the employee's ID (which was issued to them in chronological order). Subsequently, after recommending the employee,  it shows an explanation of why each technician was picked/rejected.

Evene if no one qualifies, it says so and explains why. It also handles  one change scenario: if a technician becomes unavailable after being assigned jobs, those jobs are flagged and can be reassigned to someone else.


TECH
----
Python - scheduling logic (Standard library, sqlite3, datetime).

Flask - web app and routes.

SQLite - storage, with a normalised schema (technicians, seperate skills table, jobs, assignments).

HTML/CSS - plain templates, no JavaScript framework.

NO AI and no external APIs, the point is that the decisions are strict, explainable rules.

Limitations
-----------
1) Single day only scheduler - times are compared wthin one day; there are no calendar dates yet as this is only a prototype.
2) One skill required per job - a job needs a single qualification, not a combination, so a specialised job which requires more than one skill, cannot be created, as each job attends to a certain skill in my prototype.
3) No Login.

WHAT I WOULD ADD NEXT
---------------------
1) Calendar dates for multi-scheduling.
2) Job priority for when jobs compete for the same technician
3) Service are as a tiebreaker (its sorted but not used in the decision yet)


LINK
----
https://technician-scheduler-grbp.onrender.com/
