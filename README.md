# D&D Tracker
D&D Tracker is a comprehensive Dungeons & Dragons campaign management application built with Django. It provides an intuitive interface for Dungeon Masters and players to organize campaigns, manage characters, track combat encounters, and maintain detailed session notes. The app features a clean dashboard with campaign overviews and comprehensive encounter management capabilities.

## Features
- **User Authentication**: Secure login/registration system with mandatory two-factor authentication (2FA)
- **Two-Factor Authentication**: TOTP-based 2FA using authenticator apps (Google Authenticator, Authy, etc.) with backup codes
- **Campaign Management**: Create and manage D&D campaigns with detailed descriptions and character requirements
- **Player Character Tracking**: Comprehensive character management with class, race, level, and background information
- **Monster Database**: Complete monster statistics including ability scores, combat features, and special abilities
- **Combat Encounter System**: Real-time combat tracking with initiative order, hit point management, and turn-based gameplay
- **Game Session Management**: Session planning and note-taking with chronological organization
- **Combat Session Tracking**: Active combat management with rounds, turns, and participant status
- **Hit Point Management**: Real-time HP tracking for all combat participants
- **Initiative Order Management**: Automatic turn order based on initiative rolls
- **Responsive Design**: Mobile-friendly interface for on-the-go campaign management
- **Data Organization**: Structured campaign hierarchy with players, sessions, and encounters
- **Search & Filtering**: Advanced search and filtering capabilities for campaigns and characters

## Tech Stack
- **Backend**: Django 4.2.23 (Python web framework)
- **Database**: PostgreSQL with psycopg2 adapter
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django's built-in authentication system with mandatory 2FA
- **2FA Implementation**: pyotp for TOTP generation, qrcode for QR code generation
- **Styling**: Custom CSS with responsive design
- **Environment Management**: python-dotenv for configuration
- **Testing**: Factory Boy and Faker for test data generation
- **Date Handling**: Built-in Django date utilities for session tracking

## Getting Started

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- pip (Python package installer)
- Authenticator app (Google Authenticator, Authy, Microsoft Authenticator, or similar)

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/danielsarney/dnd-tracker.git
   cd dnd-tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the `.env.example` file and fill in your database details:
   ```bash
   cp .env.example .env
   ```

5. **Set up PostgreSQL database**
   - Create a new PostgreSQL database
   - Update the `.env` file with your database credentials

6. **Run database migrations**
   ```bash
   python3 manage.py migrate
   ```

7. **Run the development server**
   ```bash
   python3 manage.py runserver
   ```

8. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

9. **Run Tests**
    ```
    python3 manage.py test
    ```