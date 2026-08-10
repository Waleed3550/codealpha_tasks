# CodeAlpha Social Media App

## Overview
A comprehensive, professional social media web application built to facilitate connections, share content, and discover opportunities. This project serves as a full-stack web application inspired by professional networking platforms like LinkedIn. It features user authentication, profile management, a dynamic feed for posts and stories, user-to-user messaging, and a job board.

## Tech Stack
### Frontend
- **React (v19)**: Component-based UI development.
- **Vite**: Next-generation frontend tooling for rapid development.
- **React Router Dom**: For seamless client-side routing.
- **Axios**: Promise-based HTTP client for API requests.
- **Lucide React**: Beautiful, consistent icon set.

### Backend
- **Django**: High-level Python web framework.
- **Django REST Framework (DRF)**: Powerful toolkit for building Web APIs.
- **Simple JWT**: JSON Web Token authentication for DRF.
- **SQLite**: Lightweight, disk-based database for development.
- **django-cors-headers**: Handling Cross-Origin Resource Sharing (CORS).

## Core Features
- **User Authentication & Security**: Secure registration, login, and token-based authentication using JWT.
- **Professional Profiles**: Detailed user profiles including avatars, bio, headline, experience, education, and skills.
- **Networking System**: Send, accept, and manage connection requests between users to build a professional network.
- **Dynamic Feed (Posts & Comments)**: Create and view posts with text, images, and videos. Engage with content through likes and comments.
- **Stories**: Ephemeral content sharing (images/videos) similar to modern social platforms.
- **Direct Messaging**: Direct user-to-user messaging system for private communication.
- **Job Board**: Post and explore job opportunities within the network.

## Prerequisites
- **Node.js** (v18 or higher recommended)
- **Python** (v3.8 or higher)
- **npm** (Node Package Manager)

## Installation & Setup

1. **Navigate to the project directory**:
   ```bash
   cd "social app"
   ```

2. **Backend Setup**:
   - Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - **Windows**: `venv\Scripts\activate`
     - **Mac/Linux**: `source venv/bin/activate`
   - Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - Run database migrations:
     ```bash
     cd socialmedia_backend
     python manage.py makemigrations
     python manage.py migrate
     ```
   - Create a superuser (optional, for admin panel access):
     ```bash
     python manage.py createsuperuser
     ```

3. **Frontend Setup**:
   - Open a new terminal and navigate to the `client` directory:
     ```bash
     cd client
     ```
   - Install npm packages:
     ```bash
     npm install
     ```

## Running the Application

### Quick Start (Windows Only)
For convenience, a `start_app.bat` script is provided to launch both the backend and frontend simultaneously. Simply double-click `start_app.bat` or run it from the command line:
```cmd
start_app.bat
```

### Manual Start
**1. Start the Backend**:
```bash
# Ensure your virtual environment is activated
cd socialmedia_backend
python manage.py runserver
```
*The backend API will be available at `http://127.0.0.1:8000/`*

**2. Start the Frontend**:
```bash
# In a new terminal
cd client
npm run dev
```
*The frontend application will be accessible at `http://localhost:5173/`*

## Project Structure
```text
.
├── client/                 # React frontend application
│   ├── public/             # Static assets
│   ├── src/                # React source code (components, pages, etc.)
│   └── package.json        # Frontend dependencies
├── socialmedia_backend/    # Django backend application
│   ├── core/               # Main Django app (Models, Views, URLs, Serializers)
│   ├── socialmedia_backend/# Django project settings
│   └── manage.py           # Django entry point
├── requirements.txt        # Python backend dependencies
└── start_app.bat           # Windows launcher script
```
username:codealpha
password:code123

