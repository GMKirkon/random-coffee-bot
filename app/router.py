from aiogram import Router, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from botspot import commands_menu
from botspot.utils import send_safe
import os
from .services.database import DatabaseService
from .models.person import Person
from ._app import App
from dotenv import load_dotenv

router = Router()
app = App()

# Load environment variables
load_dotenv()

# For debugging
mongo_conn_str = os.getenv("BOTSPOT_MONGO_DATABASE_CONN_STR", "mongodb://admin:pass@mongodb:27017/admin?authSource=admin")
mongo_db_name = os.getenv("BOTSPOT_MONGO_DATABASE_DATABASE", "random_bot")
print(f"Using MongoDB connection string: {mongo_conn_str}")
print(f"Using MongoDB database name: {mongo_db_name}")

# Initialize database service
db_service = DatabaseService(
    connection_string=mongo_conn_str,
    database_name=mongo_db_name
)

@commands_menu.add_command("start", "Start the bot")
@router.message(CommandStart())
async def start_handler(message: Message):
    await send_safe(
        message.chat.id,
        f"Hello, {html.bold(message.from_user.full_name)}!\n"
        f"Welcome to Random Person Bot!\n"
        f"Use /help to see available commands.",
    )

@commands_menu.add_command("help", "Show this help message")
@router.message(Command("help"))
async def help_handler(message: Message):
    await send_safe(
        message.chat.id,
        "Available commands:\n"
        "/add @username [tags...] - Add a person to the database with optional tags\n"
        "/delete @username - Delete a person from the database\n"
        "/random [tags] - Get a random person (optionally filtered by tags)\n"
        "/add_tags @username tag1 tag2 ... - Add multiple tags to a person\n"
        "/list - List all persons in the database\n"
        "/list_by_tags tag1 tag2 ... - List all persons that have ALL the specified tags"
    )

@commands_menu.add_command("add", "Add a person to the database")
@router.message(Command("add"))
async def add_handler(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await send_safe(message.chat.id, "Please provide a username: /add @username [tags...]")
        return

    parts = message.text.split()
    username = parts[1].strip("@")
    tags = parts[2:] if len(parts) > 2 else None

    try:
        person = await db_service.add_person(username, tags)
        tags_str = ", ".join(person.tags) if person.tags else "no tags"
        await send_safe(message.chat.id, f"Added {html.bold(username)} to the database with tags: {tags_str}")
    except Exception as e:
        await send_safe(message.chat.id, f"Error adding person: {str(e)}")

@commands_menu.add_command("add_tags", "Add multiple tags to a person")
@router.message(Command("add_tags"))
async def add_tags_handler(message: Message):
    if not message.text or len(message.text.split()) < 3:
        await send_safe(message.chat.id, "Please provide a username and at least one tag: /add_tags @username tag1 tag2 ...")
        return

    parts = message.text.split()
    username = parts[1].strip("@")
    tags = parts[2:]

    if await db_service.add_tags(username, tags):
        tags_str = ", ".join(tags)
        await send_safe(message.chat.id, f"Added tags '{html.bold(tags_str)}' to {html.bold(username)}!")
    else:
        await send_safe(message.chat.id, f"Person {html.bold(username)} not found in database.")

@commands_menu.add_command("delete", "Delete a person from the database")
@router.message(Command("delete"))
async def delete_handler(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await send_safe(message.chat.id, "Please provide a username: /delete @username")
        return

    username = message.text.split()[1].strip("@")
    if await db_service.delete_person(username):
        await send_safe(message.chat.id, f"Deleted {html.bold(username)} from the database!")
    else:
        await send_safe(message.chat.id, f"Person {html.bold(username)} not found in database.")

@commands_menu.add_command("random", "Get a random person")
@router.message(Command("random"))
async def random_handler(message: Message):
    # Extract tags from command if any
    parts = message.text.split()
    tags = parts[1:] if len(parts) > 1 else None
    
    person = await db_service.get_random_person(tags)
    if person:
        tags_str = ", ".join(person.tags) if person.tags else "no tags"
        await send_safe(
            message.chat.id,
            f"Random person: {html.bold(person.username)}\n"
            f"Tags: {tags_str}"
        )
    else:
        await send_safe(
            message.chat.id,
            "No matching persons found in database."
        )

@commands_menu.add_command("list", "List all persons in the database")
@router.message(Command("list"))
async def list_handler(message: Message):
    persons = await db_service.get_all_persons()
    if not persons:
        await send_safe(message.chat.id, "No persons found in database.")
        return

    response = "Persons in database:\n\n"
    for person in persons:
        tags_str = ", ".join(person.tags) if person.tags else "no tags"
        response += f"• {html.bold(person.username)} (tags: {tags_str})\n"

    await send_safe(message.chat.id, response)

@commands_menu.add_command("list_by_tags", "List all persons with ALL the specified tags")
@router.message(Command("list_by_tags"))
async def list_by_tags_handler(message: Message):
    if not message.text or len(message.text.split()) < 2:
        await send_safe(message.chat.id, "Please provide at least one tag: /list_by_tags tag1 [tag2 tag3 ...]")
        return

    tags = message.text.split()[1:]
    persons = await db_service.get_all_persons_by_tags(tags)
    
    if not persons:
        tags_str = ", ".join(f"'{html.bold(tag)}'" for tag in tags)
        await send_safe(message.chat.id, f"No persons found with all tags: {tags_str}")
        return

    tags_str = ", ".join(f"'{html.bold(tag)}'" for tag in tags)
    response = f"Persons with all tags {tags_str}:\n\n"
    for person in persons:
        response += f"• {html.bold(person.username)}\n"

    await send_safe(message.chat.id, response)
