from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import database
import scheduler

app = Flask(__name__)


@app.route("/")
def schedule():
    """Show all technicians, their skills, availability and bookings."""
    technicians = database.load_technicians_with_bookings()
    return render_template("schedule.html", technicians=technicians)

@app.route("/create-job", methods=["GET", "POST"])
def create_job():
    """Show the job form (GET) and save a submitted job (POST)."""
    if request.method == "POST":
        # Read the submitted form values (all arrive as text).
        job_type = request.form["job_type"]
        required_skill = request.form["required_skill"]
        suburb = request.form["suburb"]
        start_text = request.form["start_time"]
        duration_text = request.form["duration"]

        # Validate and convert. If anything is wrong, show the form again with an error.
        try:
            start = datetime.strptime(start_text, "%H:%M").time()
            duration_hours = float(duration_text)
            if duration_hours <= 0:
                raise ValueError("Duration must be positive.")
        except ValueError:
            return render_template(
                "create_job.html",
                error="Please enter a valid time (HH:MM) and a positive duration.",
            )

        # Calculate end time = start + duration.
        start_dt = datetime.combine(datetime.today(), start)
        end_dt = start_dt + timedelta(hours=duration_hours)
        end = end_dt.time()

        # Build the job dict and save it.
        job = {
            "job_type": job_type,
            "required_skill": required_skill,
            "suburb": suburb,
            "start": start,
            "end": end,
        }
        database.save_job(job)

        # After saving, send the manager back to the schedule.
        return redirect("/")

    # GET request: just show the empty form.
    return render_template("create_job.html")


@app.route("/jobs")
def jobs():
    """List all created jobs, each linking to its recommendation."""
    all_jobs = database.load_jobs()
    return render_template("jobs.html", jobs=all_jobs)


@app.route("/recommend/<int:job_id>", methods=["GET", "POST"])
def recommend(job_id):
    """Run the scheduler for one job (GET); confirm the assignment (POST)."""
    job = database.load_job(job_id)
    if job is None:
        return "Job not found.", 404

    if request.method == "POST":
        # Manager clicked Confirm. Re-validate and save.
        technician_id = int(request.form["technician_id"])
        saved = database.confirm_assignment(job, technician_id)
        if not saved:
            # The tech is no longer valid (e.g. a conflict appeared). Re-run and explain.
            technicians = database.load_technicians_with_bookings()
            recommended, eligible, rejected = scheduler.recommend_technician(job, technicians)
            explanation = ("That technician is no longer available (a conflicting booking "
                           "exists). Here is the current recommendation:\n\n"
                           + scheduler.build_explanation(job, recommended, eligible, rejected))
            return render_template("recommend.html", job=job,
                                   recommended=recommended, explanation=explanation)
        return redirect("/")

    # GET: run the engine and show the recommendation + explanation.
    technicians = database.load_technicians_with_bookings()
    recommended, eligible, rejected = scheduler.recommend_technician(job, technicians)
    explanation = scheduler.build_explanation(job, recommended, eligible, rejected)
    return render_template("recommend.html", job=job,
                           recommended=recommended, explanation=explanation)


if __name__ == "__main__":
    app.run(debug=True)