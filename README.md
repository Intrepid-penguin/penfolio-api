# MyJournal API

A secure, feature-rich backend API for a personal journaling application. Built with **Django** and **Django Ninja**, it provides a robust set of endpoints for creating, managing, and securing journal entries.

This API is designed to be consumed by a separate frontend client (e.g., a web app built with React/Vue, or a mobile application). It features JWT-based authentication, PIN-protected "Covert" journals, gamified journaling streaks, and social media integration.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.x-green.svg)](https://www.djangoproject.com/)
[![Django Ninja](https://img.shields.io/badge/api-django--ninja-lightgrey.svg)](https://django-ninja.rest-framework.com/)

---

## ✨ Core Features

*   **Secure User Authentication**:
    *   Register with email/username and password.
    *   JWT (JSON Web Token) based login for stateless sessions.
    *   Twitter OAuth2 for social login.
    *   Endpoints for email verification and password reset (requires email backend setup).
*   **Complete Journal Management (CRUD)**:
    *   Create, Read, Update, and Delete journal entries.
    *   Paginated lists for efficient data retrieval.
*   **Mood Tagging**: Categorize journals as 'Merry', 'Gloomy', or 'Covert'.
*   **PIN-Protected "Covert" Journals**: A standout privacy feature.
    *   Users must set a 4-digit PIN on their profile.
    *   A valid PIN is required to list all covert journals.
    *   A valid PIN is required to view the content of a single covert journal.
*   **Gamification with Journaling Streaks**:
    *   Automatically tracks `current_streak` and `longest_streak` for consecutive days of journaling to encourage user engagement.
*   **Powerful Search**: Full-text search across journal titles and content.
*   **Social Media Integration**:
    *   Generate a tweet based on a journal's content.
    *   Optionally provide a Twitter handle to "inspire" the tone of the generated tweet.
*   **Rich Content**:
    *   Support for Markdown in journal content.
    *   Image uploads directly to **Cloudinary**.
*   **Automatic API Documentation**: Interactive Swagger UI and ReDoc documentation generated automatically by Django Ninja.

## 🛠️ Technology Stack

*   **Backend**: Django 4.x
*   **API Framework**: Django Ninja
*   **Authentication**: Django Ninja JWT (for token-based auth), Python Social Auth (for Twitter OAuth)
*   **Database**: PostgreSQL (recommended), SQLite3 (for development)
*   **Image Storage**: Cloudinary
*   **Data Validation**: Pydantic (via Django Ninja)

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine for development and testing.

### 1. Prerequisites

*   Python 3.9+
*   Poetry or Pip for package management
*   A Cloudinary account for image uploads
*   An active email service (like SendGrid, Mailgun, or Gmail for development) for password resets.

### 2. Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/myjournal-api.git
    cd myjournal-api
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root directory. You can copy the example below and fill in your own credentials.
    ```ini
    # .env

    # Django Settings
    SECRET_KEY='your-strong-django-secret-key'
    DEBUG=True

    # Database Settings (PostgreSQL example)
    DB_NAME='myjournal_db'
    DB_USER='your_db_user'
    DB_PASSWORD='your_db_password'
    DB_HOST='localhost'
    DB_PORT='5432'

    # Cloudinary Credentials for image uploads
    CLOUDINARY_CLOUD_NAME='your-cloud-name'
    CLOUDINARY_API_KEY='your-api-key'
    CLOUDINARY_API_SECRET='your-api-secret'

    # Email Settings (Example for Gmail)
    EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST='smtp.gmail.com'
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_HOST_USER='your-email@gmail.com'
    EMAIL_HOST_PASSWORD='your-gmail-app-password' # Use an App Password, not your regular password
    ```

5.  **Run database migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create a superuser (optional):**
    ```bash
    python manage.py createsuperuser
    ```

### 3. Running the Development Server

1.  **Start the server:**
    ```bash
    python manage.py runserver
    ```
2.  **Access the API documentation:**
    The server will be running at `http://127.0.0.1:8000`. Navigate to the following URLs in your browser to see the interactive API documentation:
    *   **Swagger UI:** `http://127.0.0.1:8000/api/docs`
    *   **ReDoc:** `http://127.0.0.1:8000/api/redoc`

---

## 🔑 API Endpoints Overview

All endpoints are prefixed with `/api`.

### Users & Authentication (`/users/`)

| Method | Endpoint                    | Authentication | Description                                      |
| :----- | :-------------------------- | :------------- | :----------------------------------------------- |
| `POST` | `/register`                 | Public         | Creates a new user account.                      |
| `POST` | `/login`                    | Public         | Authenticates and returns JWT access/refresh tokens. |
| `GET`  | `/profile`                  | JWT Required   | Retrieves the authenticated user's profile.      |
| `POST` | `/profile/set-pin`          | JWT Required   | Sets or updates the user's secret PIN.           |
| `GET`  | `/auth/twitter`             | Public         | Initiates the Twitter OAuth2 login flow.         |
| `POST` | `/password/reset`           | Public         | Sends a password reset link to the user's email. |
| `POST` | `/password/reset/confirm`   | Public         | Resets the password using a token from email.    |

### Journals (`/journals/`)

| Method   | Endpoint                  | Authentication | Description                                                  |
| :------- | :------------------------ | :------------- | :----------------------------------------------------------- |
| `GET`    | `/`                       | JWT Required   | Lists all non-covert journals for the authenticated user.    |
| `POST`   | `/covert`                 | JWT Required   | Lists all covert journals (requires PIN in request body).    |
| `POST`   | `/`                       | JWT Required   | Creates a new journal entry.                                 |
| `GET`    | `/{journal_id}`           | JWT Required   | Retrieves a single journal. Hides content if covert.         |
| `POST`   | `/{journal_id}/reveal`    | JWT Required   | Reveals a covert journal's content (requires PIN).           |
| `PUT`    | `/{journal_id}`           | JWT Required   | Updates a journal entry.                                     |
| `DELETE` | `/{journal_id}`           | JWT Required   | Deletes a journal entry.                                     |
| `GET`    | `/search?q=<query>`       | JWT Required   | Searches journals by title and content.                      |
| `POST`   | `/{journal_id}/tweet`     | JWT Required   | Generates a Twitter intent URL from the journal's content.   |
| `POST`   | `/upload-image`           | JWT Required   | Uploads an image to Cloudinary and returns the URL.          |

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.