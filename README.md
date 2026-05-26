# NetDesk — Network Monitoring & IT Ticketing System

A full-stack web application for monitoring network devices and managing IT support tickets.

## Tech Stack
- **Backend**: Python + FastAPI
- **Frontend**: HTML, CSS, Bootstrap 5, Chart.js
- **Database**: SQLite (via SQLAlchemy)
- **Auth**: JWT + HTTP-only cookies
- **Monitoring**: subprocess ping (cross-platform)

## Features
- 🔐 JWT authentication with role-based access (Admin / Technician / Viewer)
- 📡 Real-time device ping monitoring (online/offline detection)
- 🎫 IT helpdesk ticket system with priorities and status tracking
- 🔔 Automatic alert generation on device outages
- 📊 Analytics dashboard with Chart.js visualizations
- 📝 Activity log for all system actions

## Setup & Installation

### 1. Clone and set up
```bash
cd netdesk
python -m venv venv
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Run the application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the system
Open: http://localhost:8000

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Technician | tech1 | tech123 |

## Project Structure
```
netdesk/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy setup
│   ├── models/
│   │   ├── user.py
│   │   ├── device.py
│   │   ├── ticket.py
│   │   └── alert.py         # Alert + ActivityLog
│   ├── routes/
│   │   ├── auth.py          # Login, register, logout
│   │   ├── devices.py       # Device CRUD + ping
│   │   ├── tickets.py       # Ticket CRUD
│   │   └── dashboard.py     # Dashboard + chart API
│   ├── services/
│   │   ├── monitor.py       # Ping engine
│   │   └── analytics.py     # Stats & chart data
│   ├── templates/           # Jinja2 HTML templates
│   └── utils/
│       └── helpers.py       # Auth helpers
├── requirements.txt
└── .env
```

## Role Permissions
| Action | Admin | Technician | Viewer |
|--------|-------|-----------|--------|
| View dashboard | ✅ | ✅ | ✅ |
| Add devices | ✅ | ✅ | ❌ |
| Delete devices | ✅ | ❌ | ❌ |
| Create tickets | ✅ | ✅ | ✅ |
| Update tickets | ✅ | ✅ | ❌ |
| Delete tickets | ✅ | ❌ | ❌ |

## Deployment (Render / Railway)
1. Push to GitHub
2. Connect repo to Render or Railway
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set SECRET_KEY environment variable

## Future Upgrades
- WebSocket real-time updates
- Email/SMS notifications
- SNMP monitoring
- Docker support
- AI issue prediction
