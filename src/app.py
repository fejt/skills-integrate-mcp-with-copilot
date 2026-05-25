"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from pathlib import Path
import json
from typing import Dict, List

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")

DATA_FILE = current_dir / "activities.json"


class Activity(BaseModel):
    description: str
    schedule: str
    max_participants: int
    participants: List[EmailStr] = []


def default_activities() -> Dict[str, Activity]:
    return {
        "Chess Club": Activity(
            description="Learn strategies and compete in chess tournaments",
            schedule="Fridays, 3:30 PM - 5:00 PM",
            max_participants=12,
            participants=["michael@mergington.edu", "daniel@mergington.edu"]
        ),
        "Programming Class": Activity(
            description="Learn programming fundamentals and build software projects",
            schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            max_participants=20,
            participants=["emma@mergington.edu", "sophia@mergington.edu"]
        ),
        "Gym Class": Activity(
            description="Physical education and sports activities",
            schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            max_participants=30,
            participants=["john@mergington.edu", "olivia@mergington.edu"]
        ),
        "Soccer Team": Activity(
            description="Join the school soccer team and compete in matches",
            schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            max_participants=22,
            participants=["liam@mergington.edu", "noah@mergington.edu"]
        ),
        "Basketball Team": Activity(
            description="Practice and play basketball with the school team",
            schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            max_participants=15,
            participants=["ava@mergington.edu", "mia@mergington.edu"]
        ),
        "Art Club": Activity(
            description="Explore your creativity through painting and drawing",
            schedule="Thursdays, 3:30 PM - 5:00 PM",
            max_participants=15,
            participants=["amelia@mergington.edu", "harper@mergington.edu"]
        ),
        "Drama Club": Activity(
            description="Act, direct, and produce plays and performances",
            schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            max_participants=20,
            participants=["ella@mergington.edu", "scarlett@mergington.edu"]
        ),
        "Math Club": Activity(
            description="Solve challenging problems and participate in math competitions",
            schedule="Tuesdays, 3:30 PM - 4:30 PM",
            max_participants=10,
            participants=["james@mergington.edu", "benjamin@mergington.edu"]
        ),
        "Debate Team": Activity(
            description="Develop public speaking and argumentation skills",
            schedule="Fridays, 4:00 PM - 5:30 PM",
            max_participants=12,
            participants=["charlotte@mergington.edu", "henry@mergington.edu"]
        )
    }


def load_activities() -> Dict[str, Activity]:
    if not DATA_FILE.exists():
        save_activities(default_activities())

    try:
        raw_data = json.loads(DATA_FILE.read_text())
        return {name: Activity(**activity) for name, activity in raw_data.items()}
    except (json.JSONDecodeError, TypeError, ValueError):
        save_activities(default_activities())
        return default_activities()


def save_activities(data: Dict[str, Activity]) -> None:
    json_data = {name: activity.dict() for name, activity in data.items()}
    DATA_FILE.write_text(json.dumps(json_data, indent=2))


activities = load_activities()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return {name: activity.dict() for name, activity in activities.items()}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: EmailStr):
    """Sign up a student for an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    activity.participants.append(email)
    save_activities(activities)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: EmailStr):
    """Unregister a student from an activity"""
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]

    if email not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    activity.participants.remove(email)
    save_activities(activities)
    return {"message": f"Unregistered {email} from {activity_name}"}
