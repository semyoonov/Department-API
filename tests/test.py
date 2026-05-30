import requests

URL = "http://localhost:8000"

def test():
    r = requests.post(f"{URL}/departments/", json={"name": "Test"})
    assert r.status_code == 200
    dept_id = r.json()["id"]

    r = requests.post(f"{URL}/departments/{dept_id}/employees/",
                      json={"full_name": "Ivan", "position": "Dev"})
    assert r.status_code == 200

    r = requests.get(f"{URL}/departments/{dept_id}")
    assert r.status_code == 200
    assert len(r.json()["employees"]) == 1

    r = requests.patch(f"{URL}/departments/{dept_id}", json={"name": "Updated"})
    assert r.json()["name"] == "Updated"

    r = requests.delete(f"{URL}/departments/{dept_id}?mode=cascade")
    assert r.status_code == 204

    r = requests.get(f"{URL}/departments/{dept_id}")
    assert r.status_code == 404