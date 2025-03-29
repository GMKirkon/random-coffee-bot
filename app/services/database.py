from typing import List, Optional
import random
from motor.motor_asyncio import AsyncIOMotorClient
from ..models.person import Person
from bson import ObjectId
from datetime import datetime

class DatabaseService:
    def __init__(self, connection_string: str, database_name: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db.persons

    async def initialize(self):
        """Initialize the database with required collections and indexes"""
        # Create unique index on username
        await self.collection.create_index("username", unique=True)

    async def add_person(self, username: str, tags: Optional[List[str]] = None) -> Person:
        try:
            # Create person without _id first
            person_dict = {
                "username": username,
                "tags": tags or [],
                "created_at": datetime.utcnow()
            }
            result = await self.collection.insert_one(person_dict)
            
            # Now create the full person object with the generated _id
            person_dict["_id"] = str(result.inserted_id)
            return Person(**person_dict)
        except Exception as e:
            if "duplicate key error" in str(e):
                raise ValueError(f"Person with username {username} already exists")
            raise

    async def add_tags(self, username: str, tags: List[str]) -> bool:
        """Add multiple tags to a person"""
        result = await self.collection.update_one(
            {"username": username},
            {"$addToSet": {"tags": {"$each": tags}}}
        )
        return result.modified_count > 0

    async def delete_person(self, username: str) -> bool:
        result = await self.collection.delete_one({"username": username})
        return result.deleted_count > 0

    async def get_random_person(self, tags: Optional[List[str]] = None) -> Optional[Person]:
        query = {}
        if tags:
            query["tags"] = {"$in": tags}
        
        count = await self.collection.count_documents(query)
        if count == 0:
            return None
            
        random_index = random.randint(0, count - 1)
        cursor = self.collection.find(query).skip(random_index).limit(1)
        person_dict = await cursor.next()
        if person_dict and "_id" in person_dict:
            person_dict["_id"] = str(person_dict["_id"])
        return Person(**person_dict) if person_dict else None

    async def add_tag(self, username: str, tag: str) -> bool:
        result = await self.collection.update_one(
            {"username": username},
            {"$addToSet": {"tags": tag}}
        )
        return result.modified_count > 0

    async def get_person(self, username: str) -> Optional[Person]:
        person_dict = await self.collection.find_one({"username": username})
        if person_dict and "_id" in person_dict:
            person_dict["_id"] = str(person_dict["_id"])
        return Person(**person_dict) if person_dict else None

    async def cleanup(self):
        """Clean up the database - used for testing"""
        await self.collection.delete_many({})
        await self.collection.drop_indexes()

    async def get_all_persons(self) -> List[Person]:
        """Get all persons from the database"""
        cursor = self.collection.find()
        persons = []
        async for person_dict in cursor:
            if person_dict and "_id" in person_dict:
                person_dict["_id"] = str(person_dict["_id"])
            persons.append(Person(**person_dict))
        return persons

    async def get_all_persons_by_tag(self, tag: str) -> List[Person]:
        """Get all persons that have a specific tag"""
        cursor = self.collection.find({"tags": tag})
        persons = []
        async for person_dict in cursor:
            if person_dict and "_id" in person_dict:
                person_dict["_id"] = str(person_dict["_id"])
            persons.append(Person(**person_dict))
        return persons 