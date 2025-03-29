import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.database import DatabaseService
from app.models.person import Person
from pytest_asyncio import fixture

@fixture
async def db_service():
    # Use test database with unique name for isolation
    service = DatabaseService("mongodb://admin:pass@localhost:27017/admin?authSource=admin", "test_db")
    
    # Initialize database
    await service.cleanup()  # Clean up any existing data
    await service.initialize()  # Set up indexes
    
    yield service
    
    # Cleanup after test
    await service.cleanup()

@pytest.mark.asyncio
async def test_add_person(db_service):
    person = await db_service.add_person("test_user")
    assert person.username == "test_user"
    assert person.tags == []
    assert person.id is not None

@pytest.mark.asyncio
async def test_delete_person(db_service):
    await db_service.add_person("test_user")
    result = await db_service.delete_person("test_user")
    assert result is True
    person = await db_service.get_person("test_user")
    assert person is None

@pytest.mark.asyncio
async def test_get_random_person(db_service):
    # Add multiple persons
    await db_service.add_person("user1")
    await db_service.add_person("user2")
    await db_service.add_person("user3")
    
    person = await db_service.get_random_person()
    assert person is not None
    assert person.username in ["user1", "user2", "user3"]

@pytest.mark.asyncio
async def test_add_tag(db_service):
    await db_service.add_person("test_user")
    result = await db_service.add_tag("test_user", "developer")
    assert result is True
    
    person = await db_service.get_person("test_user")
    assert "developer" in person.tags

@pytest.mark.asyncio
async def test_get_random_person_with_tags(db_service):
    await db_service.add_person("user1")
    await db_service.add_tag("user1", "developer")
    
    await db_service.add_person("user2")
    await db_service.add_tag("user2", "designer")
    
    person = await db_service.get_random_person(tags=["developer"])
    assert person is not None
    assert person.username == "user1"

@pytest.mark.asyncio
async def test_duplicate_username(db_service):
    # First addition should succeed
    await db_service.add_person("test_user")
    
    # Second addition should fail
    with pytest.raises(ValueError, match="Person with username test_user already exists"):
        await db_service.add_person("test_user")

@pytest.mark.asyncio
async def test_get_all_persons(db_service):
    # Add multiple persons
    await db_service.add_person("user1")
    await db_service.add_person("user2")
    await db_service.add_person("user3")
    
    persons = await db_service.get_all_persons()
    assert len(persons) == 3
    usernames = {p.username for p in persons}
    assert usernames == {"user1", "user2", "user3"}

@pytest.mark.asyncio
async def test_add_person_with_tags(db_service):
    person = await db_service.add_person("test_user", ["developer", "python"])
    assert person.username == "test_user"
    assert person.tags == ["developer", "python"]
    assert person.id is not None

@pytest.mark.asyncio
async def test_add_tags(db_service):
    # First add a person
    await db_service.add_person("test_user")
    
    # Add multiple tags
    result = await db_service.add_tags("test_user", ["developer", "python", "backend"])
    assert result is True
    
    # Verify tags were added
    person = await db_service.get_person("test_user")
    assert set(person.tags) == {"developer", "python", "backend"}
    
    # Try adding some of the same tags again (should not duplicate)
    result = await db_service.add_tags("test_user", ["developer", "python"])
    assert result is False  # False because no new tags were added
    
    # Verify no duplicates were added
    person = await db_service.get_person("test_user")
    assert set(person.tags) == {"developer", "python", "backend"}
    
    # Try adding a mix of new and existing tags
    result = await db_service.add_tags("test_user", ["developer", "new_tag"])
    assert result is True  # True because at least one new tag was added
    
    # Verify the new tag was added
    person = await db_service.get_person("test_user")
    assert set(person.tags) == {"developer", "python", "backend", "new_tag"}
    
    # Try adding tags to non-existent person
    result = await db_service.add_tags("nonexistent", ["tag1", "tag2"])
    assert result is False

@pytest.mark.asyncio
async def test_get_all_persons_by_tags(db_service):
    # Add persons with different combinations of tags
    await db_service.add_person("user1", ["developer", "python", "backend"])
    await db_service.add_person("user2", ["developer", "javascript", "frontend"])
    await db_service.add_person("user3", ["developer", "python", "frontend"])
    await db_service.add_person("user4", ["designer", "ui", "ux"])
    
    # Test getting persons with a single tag
    python_devs = await db_service.get_all_persons_by_tags(["python"])
    assert len(python_devs) == 2
    python_usernames = {p.username for p in python_devs}
    assert python_usernames == {"user1", "user3"}
    
    # Test getting persons with multiple tags
    python_backend_devs = await db_service.get_all_persons_by_tags(["python", "backend"])
    assert len(python_backend_devs) == 1
    assert python_backend_devs[0].username == "user1"
    
    # Test getting persons with multiple tags in different order
    backend_python_devs = await db_service.get_all_persons_by_tags(["backend", "python"])
    assert len(backend_python_devs) == 1
    assert backend_python_devs[0].username == "user1"
    
    # Test with no matching tags combination
    no_matches = await db_service.get_all_persons_by_tags(["python", "ux"])
    assert len(no_matches) == 0
    
    # Test with non-existent tag
    non_existent = await db_service.get_all_persons_by_tags(["nonexistent"])
    assert len(non_existent) == 0 