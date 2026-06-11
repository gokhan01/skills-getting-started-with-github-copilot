from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")

    response = client.post(f"/activities/{encoded_activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]


def test_signup_rejects_duplicate_student(client):
    response = client.post(
        f"/activities/{quote('Programming Class', safe='')}/signup",
        params={"email": "emma@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_fails_for_unknown_activity(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success_with_case_insensitive_email(client):
    response = client.delete(
        f"/activities/{quote('Music Club', safe='')}/participants",
        params={"email": "AVA@MERGINGTON.EDU"},
    )

    assert response.status_code == 200
    assert "Unregistered ava@mergington.edu from Music Club" in response.json()["message"]

    activities_after_delete = client.get("/activities").json()
    assert "ava@mergington.edu" not in activities_after_delete["Music Club"]["participants"]


def test_unregister_fails_for_unknown_participant(client):
    response = client.delete(
        f"/activities/{quote('Science Club', safe='')}/participants",
        params={"email": "not-here@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_fails_for_unknown_activity(client):
    response = client.delete("/activities/Unknown%20Club/participants", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
