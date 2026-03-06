# Flask + PostgreSQL Backend

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/taboo_db
SECRET_KEY=your-secret-key
```

4. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Run

### Development
```bash
python run.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Structure

```
backend/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration
│   ├── extensions.py        # Extensions (db, migrate)
│   ├── middlewares/         # Middlewares
│   │   └── auth.py          # JWT authentication (@token_required)
│   ├── models/              # Database models
│   │   ├── user.py          # User
│   │   ├── game.py          # Game
│   │   ├── plays.py         # User participation in a game
│   │   ├── group.py         # Group inside a game
│   │   ├── member.py        # User-to-group assignment
│   │   └── word.py          # Game words
│   ├── routes/              # Routes/Endpoints
│   │   ├── login.py         # Login, signup, validation
│   │   ├── users.py         # Users CRUD
│   │   ├── games.py         # Games CRUD
│   │   └── plays.py         # Game participation
│   └── services/            # Business logic
│       ├── user.py          # User service
│       ├── game.py          # Game and group service
│       └── plays.py         # Plays service
├── migrations/              # Database migrations
│   └── versions/            # Migration versions
├── tests/                   # Pytest tests
├── run.py                   # Development entry point
└── wsgi.py                  # Production entry point
```

## Models

- **User**: System users
- **Game**: Taboo games
- **Plays**: A user's participation in a game (User-Game relationship)
- **Group**: Groups inside a game (e.g., Team A, Team B)
- **Member**: Assignment of a user to a specific group (via `play_id` and `group_id`)
- **Word**: Taboo game words

## Endpoints

### Authentication
- `POST /users` - Create user
- `POST /login` - Login and get JWT token
- `POST /validate` - Validate JWT token

### Games
- `POST /games` - Create game (authentication required)
- `GET /games` - List all games
- `GET /games/active` - List active games
- `PUT /games/<id>` - Update game (authentication required)
- `DELETE /games/<id>` - Delete game (authentication required)

### Plays (Participation)
- `POST /play` - Join authenticated user to a game. Body: `{"game_id": <id>}`
- `DELETE /leave` - Remove authenticated user from their active game
- `GET /plays/game/<game_id>` - List plays in a game
- `GET /plays/user` - Get authenticated user's active play
- `GET /plays` - List all plays

### Groups
- `POST /groups/assignments` - Assign user to a group (must be a player in the game)
- `PUT /groups/assignments` - Reassign user to another group (game creator only)
- `GET /groups/<game_id>` - List game groups with their members

## Authentication

The API uses JWT tokens generated with `itsdangerous`. Protected endpoints require this header:
```
Authorization: Bearer <token>
```

The `@token_required` middleware validates the token and loads the user into `g.current_user`.
