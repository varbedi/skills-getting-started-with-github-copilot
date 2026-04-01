import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_post_signup_new():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    response = client.post(path, params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_module.activities[activity_name]["participants"]


def test_post_signup_duplicate():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    response = client.post(path, params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_unregister_existing():
    activity_name = "Basketball Team"
    email = "alex@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"
    assert email in app_module.activities[activity_name]["participants"]

    response = client.delete(path, params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in app_module.activities[activity_name]["participants"]


def test_delete_non_existing_participant():
    activity_name = "Basketball Team"
    email = "unregistered@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"
    assert email not in app_module.activities[activity_name]["participants"]

    response = client.delete(path, params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_activity_not_found():
    bad_activity = "No Such Activity"
    bad_path = f"/activities/{quote(bad_activity)}/signup"
    email = "x@mergington.edu"

    post_response = client.post(bad_path, params={"email": email})
    delete_response = client.delete(bad_path, params={"email": email})

    assert post_response.status_code == 404
    assert post_response.json()["detail"] == "Activity not found"
    assert delete_response.status_code == 404
    assert delete_response.json()["detail"] == "Activity not found"
