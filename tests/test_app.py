import pytest
from httpx import AsyncClient

from src.app import app, activities


@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_get_activities(client: AsyncClient):
    response = await client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities

@pytest.mark.asyncio
async def test_signup_for_activity(client: AsyncClient):
    activity_name = "Chess Club"
    email = "test@example.com"
    response = await client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]
    # Cleanup
    activities[activity_name]["participants"].remove(email)

@pytest.mark.asyncio
async def test_signup_for_full_activity(client: AsyncClient):
    activity_name = "Chess Club"
    # Fill up the activity
    original_participants = list(activities[activity_name]["participants"])
    for i in range(len(original_participants), activities[activity_name]["max_participants"]):
        activities[activity_name]["participants"].append(f"test{i}@example.com")

    response = await client.post(f"/activities/{activity_name}/signup?email=new@example.com")
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}
    
    # Cleanup
    activities[activity_name]["participants"] = original_participants


@pytest.mark.asyncio
async def test_unregister_from_activity(client: AsyncClient):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    response = await client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
    # Cleanup
    activities[activity_name]["participants"].append(email)

@pytest.mark.asyncio
async def test_unregister_student_not_found(client: AsyncClient):
    activity_name = "Chess Club"
    email = "nonexistent@example.com"
    response = await client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not found in this activity"}
