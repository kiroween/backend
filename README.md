# TimeGrave API

> A digital time capsule for your future self and loved ones

TimeGrave is a web application that allows you to create digital time capsules that automatically unlock on a specific date. Store precious memories and messages, and when the set date arrives, listen to them as audio messages.

## ✨ Key Features

- 🔒 **Time Lock**: Time capsules that automatically unlock on a future date
- 🎙️ **Text-to-Speech**: Automatic voice conversion when unlocked (Supertone TTS)
- 👥 **Collaborative Writing**: Invite friends to write together
- 🔗 **Sharing**: Share unlocked time capsules with friends
- ☁️ **Cloud Storage**: Securely store audio files on AWS S3
- 🔐 **Security**: JWT-based authentication for privacy protection

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI |
| **Database** | SQLite / PostgreSQL (RDS) |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic |
| **Scheduler** | APScheduler (Auto-unlock at midnight daily) |
| **Cloud Storage** | AWS S3 |
| **TTS** | Supertone API |
| **Package Manager** | uv (Rust-based ultra-fast) |
| **Container** | Docker |
| **Authentication** | JWT |

## Getting Started

### Running with Docker (Recommended)

```bash
# Build and run Docker container
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Local Development (using uv)

#### Install uv

```bash
# Mac/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or install with pip
pip install uv
```

#### Run Project

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run development server
uvicorn app.main:app --reload
```

#### Why uv?

- ⚡ **10-100x Faster**: Written in Rust, much faster than pip
- 🔒 **Automatic Lock Files**: Ensures reproducible builds
- 📦 **Unified Tool**: Integrates virtual environments, package installation, and project management

## 📖 Use Cases

### 1. Message to Future Self
Write a message to yourself 1 year, 5 years in the future and set a lock
→ When the set date arrives, it automatically unlocks and you can listen to it as audio

### 2. Collaborate with Friends
Invite friends to write a time capsule together
→ Multiple people can record memories together and open them in the future

### 3. Special Message to Loved Ones
Set it to unlock on special days (birthdays, anniversaries) to deliver messages
→ Share via link with friends or copy to their account

## 🎯 Core Features

### Time Capsule Management
- **Create**: Set title, content, and unlock date
- **Auto-Unlock**: Scheduler automatically checks and unlocks at midnight (KST) daily
- **View**: Content hidden when locked, fully revealed after unlock
- **Voice Conversion**: Automatic TTS generation and S3 storage on first view after unlock

### Friend Invitation
- **Generate Invite Link**: Create unique invitation link for friends
- **Grant Write Permission**: Invited friends can write together
- **Permission Management**: Add or remove friends anytime

### Sharing
- **Generate Share Link**: Share unlocked time capsules as read-only
- **Copy Feature**: Save shared time capsules to your account
- **Audio Reuse**: Cost savings by reusing the same audio file

## 📡 API Documentation

After running the server, you can access interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### User Management
- `POST /api/users` - Sign up
- `POST /api/users/sign-in` - Sign in
- `POST /api/users/sign-out` - Sign out
- `DELETE /api/users` - Delete account

#### Time Capsule Management
- `GET /api/graves` - List my time capsules
- `POST /api/graves` - Create new time capsule
- `GET /api/graves/{id}` - Get time capsule details (auto-generates TTS on unlock)
- `POST /api/graves/unlock-check` - Manual unlock check (for testing)

#### Friend Invitation (Write Permission)
- `POST /api/graves/{id}/invite` - Generate invite link
- `POST /api/graves/invite/{invite_token}/accept` - Accept invitation
- `PATCH /api/graves/{id}/share` - Add/remove friends

#### Sharing (Read-Only)
- `POST /api/graves/{id}/share` - Generate share link
- `GET /api/graves/shared/{share_token}` - View shared time capsule
- `POST /api/graves/shared/{share_token}/copy` - Copy to my account

For detailed API specifications, see [API Documentation](docs/API_DOCUMENTATION.md).

## Environment Configuration

### Required Environment Variables

Create a `.env` file and configure the following variables:

```bash
# Database
DATABASE_URL=sqlite:///./data/timegrave.db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS S3 (TTS audio file storage)
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=timegrave-audio

# Supertone TTS API
SUPERTONE_API_KEY=your-supertone-api-key
SUPERTONE_API_URL=https://supertoneapi.com/v1/text-to-speech/a929cf8981cbfd9b8e6eb3
```

For detailed setup instructions, see [TTS and S3 Setup Guide](docs/tts-s3-setup.md).

## 📂 Project Structure

```
timegrave-api/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   └── config.py              # Environment configuration
│   ├── models/
│   │   ├── database.py            # Database connection
│   │   ├── user.py                # User model
│   │   └── tombstone.py           # Time capsule model
│   ├── schemas/
│   │   ├── user.py                # User schema
│   │   └── tombstone.py           # Time capsule schema
│   ├── repositories/              # Data access layer
│   │   ├── user_repository.py
│   │   └── tombstone_repository.py
│   ├── services/                  # Business logic
│   │   ├── user_service.py
│   │   ├── tombstone_service.py
│   │   ├── tts_service.py         # TTS voice conversion
│   │   ├── s3_service.py          # S3 upload/download
│   │   └── scheduler.py           # Auto-unlock scheduler
│   ├── routers/                   # API routers
│   └── utils/                     # Utility functions
│       ├── auth.py                # JWT authentication
│       └── response_formatter.py  # Response formatting
├── data/                          # SQLite database
├── docs/                          # Documentation
│   ├── API_DOCUMENTATION.md       # Detailed API docs
│   ├── FRIEND_WRITE_FEATURE.md    # Friend invitation guide
│   └── TTS_IMPLEMENTATION_SUMMARY.md
├── migrations/                    # Database migrations
├── tests/                         # Test code
├── deploy/                        # Deployment scripts
├── Dockerfile                     # Docker image
├── docker-compose.yml             # Docker Compose config
└── pyproject.toml                 # Project dependencies
```

## Development

### Dependency Management

```bash
# Add new package
uv pip install <package-name>

# Add dev dependency
uv pip install --dev <package-name>

# Update dependency
uv pip install --upgrade <package-name>

# Sync all dependencies
uv pip sync
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_tombstone.py

# Test TTS and S3 integration
python scripts/test_tts_s3.py
```

### Code Quality

```bash
# Lint with Ruff
ruff check .

# Auto-fix with Ruff
ruff check --fix .

# Format code
ruff format .
```

## 🔍 Key Technical Implementations

### Auto-Unlock System
- **APScheduler**: Runs automatically at midnight (KST) daily
- **Operation**: Automatically unlocks time capsules where `unlock_date <= today`
- **Timezone**: Based on Korea Standard Time (KST, UTC+9)

### Text-to-Speech Conversion
- **Generation Timing**: On first view after unlock (cost optimization)
- **Flow**: 
  1. View unlocked time capsule
  2. Generate TTS with Supertone API
  3. Upload to AWS S3
  4. Save audio_url to DB
  5. Reuse saved URL for subsequent views

### Friend Invitation System
- **Invite Link**: UUID-based unique token generation
- **Permission Management**: Store user_id in share array (JSON)
- **Duplicate Prevention**: Already invited friends cannot be re-invited

### Sharing vs Invitation
| Feature | Share (share_token) | Invite (invite_token) |
|---------|--------------------|-----------------------|
| Purpose | Read-only | Write permission |
| Access | View only | Collaborative writing |
| Copy | Available | Not needed |

## 📚 Additional Documentation

- [Detailed API Documentation](docs/API_DOCUMENTATION.md)
- [Friend Invitation Feature Guide](docs/FRIEND_WRITE_FEATURE.md)
- [Friend Invitation Testing Guide](TEST_INVITE_FEATURE.md)
- [TTS Implementation Summary](docs/TTS_IMPLEMENTATION_SUMMARY.md)
- [TTS and S3 Setup Guide](docs/tts-s3-setup.md)
- [EC2 Deployment Guide](docs/README.md)
- [RDS Migration Guide](docs/rds-migration.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

Issues and PRs are always welcome!

## 📄 License

MIT
