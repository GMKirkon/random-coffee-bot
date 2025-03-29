# Random Coffee Bot

A Telegram bot that helps organize random coffee meetings between team members. Built with [botspot](https://github.com/calmmage/botspot) and aiogram.

## Features

- 👥 Add and manage team members
- 🏷️ Tag-based filtering for coffee matches
- 🎲 Random person selection with tag filtering
- 📊 MongoDB integration with automatic authentication
- 🔧 Easy configuration via environment variables
- ⚡ Error handling and reporting
- 🔄 CI pipeline with MongoDB service for automated testing

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/random-coffee-bot.git
cd random-coffee-bot
```

2. Install dependencies:
```bash
poetry install
```

3. Set up your environment:
```bash
cp example.env .env
# Edit .env with your bot token and settings
```

4. Start the services:
```bash
docker-compose up -d
```

5. Run the bot (choose ONE of these methods):

   a. Run in Docker (recommended):
   ```bash
   docker-compose up bot
   ```

   b. Run locally (for development):
   ```bash
   poetry run python run.py
   ```

   ⚠️ **Important**: Do not run the bot both in Docker and locally at the same time, as this will cause conflicts.

## Available Commands

- `/add @username [tags...]` - Add a person to the database with optional tags
- `/delete @username` - Delete a person from the database
- `/random [tags]` - Get a random person (optionally filtered by tags)
- `/add_tags @username tag1 tag2 ...` - Add multiple tags to a person
- `/list` - List all persons in the database
- `/list_by_tag tag` - List all persons with a specific tag

## Project Structure

```
.
├── app/
│   ├── _app.py          # Core app
│   ├── bot.py           # Bot setup & launcher
│   ├── router.py        # Bot commands and handlers
│   └── __init__.py
├── example.env         # Example environment variables
├── pyproject.toml      # Project dependencies
├── README.md
├── Dockerfile
├── docker-compose.yaml
└── run.py              # Main entry point - for docker etc.
```

## Configuration

The bot uses environment variables for configuration. Copy `example.env` to `.env` and edit the following variables:

Required variables:
- `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather

MongoDB configuration:
- `BOTSPOT_MONGO_DATABASE_ENABLED`: Set to `true` to enable MongoDB
- `BOTSPOT_MONGO_DATABASE_CONN_STR`: MongoDB connection string (default: mongodb://admin:pass@localhost:27017/admin?authSource=admin)
- `BOTSPOT_MONGO_DATABASE_DATABASE`: MongoDB database name (default: random_bot)

Other options:
- `BOTSPOT_SCHEDULER_ENABLED`: Enable event scheduler
- `BOTSPOT_USER_DATA_ENABLED`: Enable user data storage
- And more...

## MongoDB Setup

MongoDB is automatically configured with authentication when the container starts. The default credentials are:
- Username: `admin`
- Password: `pass`
- Database: `admin`
- Auth Source: `admin`

These credentials are set up in the `docker-compose.yaml` file using MongoDB's initialization environment variables:
- `MONGO_INITDB_ROOT_USERNAME`
- `MONGO_INITDB_ROOT_PASSWORD`

The bot and mongo-express services are automatically configured to use these credentials.

## Development

1. Install pre-commit hooks:
```bash
pre-commit install
```

2. Run tests:
```bash
poetry run pytest
```

3. About GitHub Actions workflow:
   - The CI pipeline automatically sets up a MongoDB service for testing
   - Tests run against this MongoDB instance with authentication
   - Environment variables are automatically configured for the test environment
   - You can see the configuration in `.github/workflows/main.yml`

## Docker Support

Build and run with Docker:

```bash
docker-compose up --build
```

## Troubleshooting

If you encounter the error "Conflict: terminated by other getUpdates request", it means multiple instances of the bot are trying to run simultaneously. To fix this:

1. Stop all running containers:
```bash
docker-compose down
```

2. Make sure you're only running the bot in one place (either in Docker or locally, not both)

3. Start the services again:
```bash
docker-compose up -d
```

4. Run the bot using one of the methods described in the Quick Start section

If you encounter MongoDB authentication errors:
1. Make sure MongoDB is running: `docker-compose ps`
2. Check if the MongoDB container is healthy: `docker-compose logs mongodb`
3. Verify your `.env` file has the correct MongoDB connection string with authentication
4. Restart the services: `docker-compose down && docker-compose up -d`

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
