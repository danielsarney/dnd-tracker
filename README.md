# D&D Tracker

D&D Tracker is a comprehensive Dungeons & Dragons campaign management application built with Django. It provides an intuitive interface for Dungeon Masters and players to organize campaigns, manage characters, track game sessions, and monitor campaign progress. The app features a clean dashboard with visual summaries and comprehensive campaign tracking capabilities.

## Features

- **User Authentication**: Secure login/registration system with user-specific data isolation and profile management
- **Campaign Management**: Create and manage multiple D&D campaigns with descriptions and DM assignments
- **Character Tracking**: Comprehensive character management including player characters, NPCs, and monsters with race, class, and background details
- **Game Session Logging**: Track game sessions with dates, summaries, and campaign association
- **Dashboard Overview**: Visual summary of campaign data with statistics and recent activity
- **Profile Management**: Custom user profiles with display names and avatar uploads
- **Responsive Design**: Mobile-friendly interface for on-the-go campaign management
- **Data Organization**: Structured data management for campaigns, characters, and sessions
- **Search & Filtering**: Advanced search and filtering capabilities for campaigns and characters
- **Campaign Analytics**: Track campaign activity, character distribution, and session frequency

## Tech Stack

- **Backend**: Django 4.2.23 (Python web framework)
- **Database**: PostgreSQL with psycopg3 adapter
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django's built-in authentication system with custom profile extension
- **Styling**: Custom CSS with responsive design
- **Environment Management**: python-dotenv for configuration
- **Testing**: Factory Boy and Faker for test data generation
- **Image Handling**: Pillow for avatar uploads and image processing
- **Date Handling**: Advanced date operations for session tracking

## Getting Started

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- pip (Python package installer)

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
   Clone the `.env.example` file to create your `.env` file:
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

9. **Access the application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

10. **Run Tests**
    ```bash
    python3 manage.py test
    ```

11. **Generate Demo Data**
    ```bash
    python3 manage.py seed
    ```