from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)
initial_activities = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def restore_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(initial_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(initial_activities))


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_adds_student_to_activity():
    response = client.post(
        "/activities/Chess Club/signup?email=teststudent@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up teststudent@mergington.edu for Chess Club"
    }
    assert "teststudent@mergington.edu" in app_module.activities["Chess Club"][
        "participants"
    ]


def test_signup_rejects_duplicate_participant():
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_full_activity():
    activity = app_module.activities["Chess Club"]
    activity["max_participants"] = len(activity["participants"])

    response = client.post(
        "/activities/Chess Club/signup?email=waitinglist@mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Robotics Club/signup?email=teststudent@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student_from_activity():
    response = client.post(
        "/activities/Chess Club/signup?email=teststudent@mergington.edu"
    )
    assert response.status_code == 200

    response = client.delete(
        "/activities/Chess Club/unregister?email=teststudent@mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Removed teststudent@mergington.edu from Chess Club"
    }
    activity = client.get("/activities").json()["Chess Club"]
    assert "teststudent@mergington.edu" not in activity["participants"]


def test_unregister_rejects_missing_participant():
    response = client.delete(
        "/activities/Chess Club/unregister?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found in activity"


def test_unregister_rejects_unknown_activity():
    response = client.delete(
        "/activities/Robotics Club/unregister?email=teststudent@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
