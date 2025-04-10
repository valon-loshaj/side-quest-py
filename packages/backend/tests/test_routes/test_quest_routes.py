import pytest

from src.side_quest_py.routes.quest_routes import quest_bp, quest_service


@pytest.fixture(autouse=True)
def reset_quest_service():
    """Reset the quest service before each test."""
    quest_service.quests = {}
    yield


def test_create_quest(client):
    """Test creating a new quest."""
    # Prepare test data
    test_data = {"title": "TestQuest"}

    # Send POST request with JSON data
    response = client.post("/api/v1/quest", json=test_data)

    # Assert response status code is 201 (Created)
    assert response.status_code == 201

    # Assert message contains the quest title
    assert f"Quest {test_data['title']} created successfully" in response.json["message"]

    # Assert quest data is returned
    assert "quest" in response.json
    assert response.json["quest"]["title"] == test_data["title"]
    assert response.json["quest"]["id"] is not None
    assert response.json["quest"]["completed"] is False


def test_create_quest_missing_title(client):
    """Test creating a quest without providing a title."""
    # Prepare bad test data
    bad_test_data = {"title": ""}

    # Send POST request with empty JSON data
    response = client.post("/api/v1/quest", json=bad_test_data)

    # Assert response status code is 400 (Bad Request)
    assert response.status_code == 400
    assert "Title for quest was not provided" in response.json["error"]


def test_get_quest_by_id(client):
    """Test getting a quest by its ID."""
    # Prepare test data
    test_data = {"title": "TestQuest"}

    # Create a quest
    response = client.post("/api/v1/quest", json=test_data)
    quest_id = response.json["quest"]["id"]

    # Send GET request with quest ID
    response = client.get(f"/api/v1/quest/{quest_id}")

    # Assert response status code is 200 (OK)
    assert response.status_code == 200

    # Assert quest data is returned
    assert "quest" in response.json
    assert response.json["quest"]["id"] == quest_id
    assert response.json["quest"]["title"] == test_data["title"]
    assert response.json["quest"]["completed"] is False


def test_get_nonexistent_quest(client):
    """Test getting a nonexistent quest."""
    # Send GET request with nonexistent quest ID
    nonexistent_id = "nonexistent_id"
    response = client.get(f"/api/v1/quest/{nonexistent_id}")

    # Assert response status code is 404 (Not Found)
    assert response.status_code == 404
    assert f"Quest with ID: {nonexistent_id} not found" in response.json["error"]


def test_get_all_quests(client):
    """Test getting all quests."""
    # Prepare test data
    test_data = [
        {"title": "TestQuest1"},
        {"title": "TestQuest2"},
        {"title": "TestQuest3"},
    ]

    # Create a quest
    for quest in test_data:
        response = client.post("/api/v1/quest", json=quest)
        assert response.status_code == 201
        assert f"Quest {quest['title']} created successfully" in response.json["message"]

    # Get all quests
    response = client.get("/api/v1/quests")
    assert response.status_code == 200
    assert len(response.json) == len(test_data)
    for quest in response.json:
        assert quest["title"] in [q["title"] for q in test_data]


def test_complete_quest(client):
    """Test completing a quest."""
    # Prepare test data
    test_data = {"title": "TestQuest"}

    # Create a quest
    response = client.post("/api/v1/quest", json=test_data)
    quest_id = response.json["quest"]["id"]

    # Send PATCH request with quest ID
    response = client.patch(f"/api/v1/quest/{quest_id}")

    # Assert response status code is 200 (OK)
    assert response.status_code == 200

    # Assert quest data is returned
    assert "quest" in response.json
    assert response.json["quest"]["id"] == quest_id
    assert response.json["quest"]["title"] == test_data["title"]
    assert response.json["quest"]["completed"] is True


def test_complete_nonexistent_quest(client):
    """Test completing a nonexistent quest."""
    # Send PATCH request with nonexistent quest ID
    nonexistent_id = "nonexistent_id"
    response = client.patch(f"/api/v1/quest/{nonexistent_id}")

    # Assert response status code is 404 (Not Found)
    assert response.status_code == 404
    assert f"Quest with ID: {nonexistent_id} not found" in response.json["error"]
