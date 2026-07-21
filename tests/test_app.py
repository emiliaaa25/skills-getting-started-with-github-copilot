from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_student_from_activity():
    response = client.post(
        "/activities/Chess Club/signup?email=teststudent@mergington.edu"
    )
    assert response.status_code == 200

    response = client.delete("/activities/Chess Club/unregister?email=teststudent@mergington.edu")
    assert response.status_code == 200

    activity = client.get("/activities").json()["Chess Club"]
    assert "teststudent@mergington.edu" not in activity["participants"]
