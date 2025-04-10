import pytest

from src.side_quest_py.routes.adventurer_routes import adventurer_bp


def test_create_adventurer(client):
    """Test creating a new adventurer."""
    # Prepare test data
    test_data = {"name": "TestAdventurer", "level": 1, "experience": 0}

    # Send POST request with JSON data
    response = client.post("/api/v1/adventurer", json=test_data)

    # Assert response status code is 201 (Created)
    assert response.status_code == 201

    # Assert message contains the adventurer name
    assert f"Adventurer {test_data['name']} created successfully" in response.json["message"]

    # Assert adventurer data is returned
    assert "adventurer" in response.json
    assert response.json["adventurer"]["name"] == test_data["name"]
    assert response.json["adventurer"]["level"] == test_data["level"]
    assert response.json["adventurer"]["experience"] == test_data["experience"]


def test_create_adventurer_missing_name(client):
    """Test creating an adventurer without providing a name."""
    # Prepare bad test data
    bad_test_data = {"name": "", "level": 1, "experience": 0}

    # Send POST request with empty JSON data
    response = client.post("/api/v1/adventurer", json=bad_test_data)

    # Assert response status code is 400 (Bad Request)
    assert response.status_code == 400
    assert "Name is required" in response.json["error"]


def test_get_adventurer(client):
    """Test retrieving an adventurer by name."""
    # First create an adventurer
    test_data = {"name": "GetTestAdventurer", "level": 2, "experience": 100}
    client.post("/api/v1/adventurer", json=test_data)

    # Try to get the adventurer
    response = client.get(f"/api/v1/adventurer/{test_data['name']}")

    # Assert response status code
    assert response.status_code == 200

    # Assert adventurer data
    assert "adventurer" in response.json
    assert response.json["adventurer"]["name"] == test_data["name"]
    assert response.json["adventurer"]["level"] == test_data["level"]
    assert response.json["adventurer"]["experience"] == test_data["experience"]


def test_get_nonexistent_adventurer(client):
    """Test retrieving a non-existent adventurer."""
    response = client.get("/api/v1/adventurer/NonExistentAdventurer")

    # Assert response status code
    assert response.status_code == 404
    assert "not found" in response.json["error"]


def test_get_all_adventurers(client):
    """Test retrieving all adventurers."""
    # Create a couple of adventurers
    client.post("/api/v1/adventurer", json={"name": "Adventurer1"})
    client.post("/api/v1/adventurer", json={"name": "Adventurer2"})

    # Get all adventurers
    response = client.get("/api/v1/adventurers")

    # Assert response status code
    assert response.status_code == 200

    # Assert adventurers data
    assert "adventurers" in response.json
    assert "count" in response.json
    assert response.json["count"] >= 2  # At least the two we created


if __name__ == "__main__":
    pytest.main()
