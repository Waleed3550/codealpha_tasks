# 🌐 LinguaVerse — AI-Powered 3D Language Translation Application

LinguaVerse is a production-ready, full-stack language translation web application built with **Python 3.11**, **Django REST Framework**, **LibreTranslate API**, **Three.js**, and **GSAP**. It features an Apple-inspired glassmorphism interface, interactive 3D WebGL background, real-time AJAX translation, text-to-speech, speech recognition voice input, PDF report exporting, light/dark mode, and persistent translation history & favorites storage.

---

## 🛠️ Tech Stack

### **Backend**
- **Language**: Python 3.11
- **Framework**: Django 5.1 & Django REST Framework (DRF) 3.15+
- **HTTP Client**: Requests 2.31+
- **Environment Management**: `python-decouple`
- **Security & Middleware**: `django-cors-headers`, `WhiteNoise` (static file compression)

### **Frontend**
- **UI Architecture**: Modular ES6 JavaScript, HTML5, CSS3
- **Design System**: Apple-inspired Glassmorphism, Neon Blue & Purple Tokens, Dark/Light Mode
- **3D Graphics**: Three.js (Equirectangular Earth, Atmosphere Glow, Starfield, Floating Particles, Mouse Parallax)
- **Animations**: GSAP 3.12 (Timelines, Entrance Reveals, Card Lifts)
- **APIs & Libraries**:
  - Web Speech Synthesis API (Text-to-Speech)
  - Web Speech Recognition API (Voice Input Microphone)
  - jsPDF 2.5 (PDF Report Exporter)

---

## 📁 Project Structure

```
language_tool/
├── LanguageTranslator/         # Django Project Settings & Routing
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # Base Decouple Settings
│   │   ├── development.py     # Local Dev Settings
│   │   └── production.py      # Production Security Settings
│   ├── asgi.py
│   ├── urls.py
│   └── wsgi.py
├── translator/                # Translator App Architecture
│   ├── services/              # Service Factory Pattern
│   │   ├── __init__.py
│   │   ├── base.py            # BaseTranslationService Contract
│   │   ├── factory.py         # Service Factory Registry
│   │   └── libretranslate.py  # LibreTranslate Implementation
│   ├── utils/
│   │   ├── response.py        # Standard API Response Wrappers
│   │   └── validators.py      # Input Validation Helpers
│   ├── exceptions.py          # Custom Translation Exception Classes
│   ├── serializers.py         # DRF Request & Response Serializers
│   ├── urls.py                # App Route Mapping
│   └── views.py               # API & Template Views
├── static/
│   ├── css/
│   │   └── main.css           # Design Tokens, Glassmorphism, Themes, Animations
│   ├── js/
│   │   └── app.js             # EarthScene, TranslationUI, ToastManager
│   └── images/
│       └── earth_texture.jpg  # 3D Globe Texture Map
├── templates/
│   └── translator/
│       └── index.html         # Main Application Template
├── .env.example               # Environment Template
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚡ Installation & Setup Instructions

### 1. **Prerequisites**
- Python 3.11+ installed.
- Git installed.

### 2. **Clone & Environment Setup**
```bash
# Navigate to workspace directory
cd language_tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure Environment Variables**
Copy the template `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and verify key settings:
```env
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=True
TRANSLATION_SERVICE=libretranslate
LIBRETRANSLATE_URL=https://libretranslate.com
TRANSLATION_TIMEOUT=30
```

### 5. **Database Migration**
Run Django database migrations:
```bash
python manage.py migrate --settings=LanguageTranslator.settings.development
```

### 6. **Run Development Server**
Start the Django development server:
```bash
python manage.py runserver --settings=LanguageTranslator.settings.development
```

Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 📡 API Documentation

### **1. POST `/translate/`**
Translates text between supported languages.

**Request Body:**
```json
{
  "text": "Hello world",
  "source_language": "en",
  "target_language": "es"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Translation completed successfully.",
  "data": {
    "translated_text": "Hola Mundo",
    "source_language": "en",
    "target_language": "es",
    "detected_language": "en",
    "characters_translated": 11
  },
  "status_code": 200
}
```

### **2. GET `/languages/`**
Retrieves the list of supported languages.

### **3. GET `/health/`**
Returns service health and reachability status.

---

## 🌟 Key Application Features

- **3D Interactive Background**: Real-time WebGL Earth rotation with mouse parallax.
- **Copy Confirmation & Animations**: Instant visual feedback on copying translation.
- **Voice Microphone Dictation**: Speech-to-text input via browser Web Speech API.
- **PDF Report Exporter**: Download styled translation reports as PDF files.
- **Dark & Light Mode**: Toggleable color themes with stored preference.
- **Settings Panel Modal**: Configure auto-translate on typing and 3D graphic options.
- **LocalStorage History & Favorites**: Persistent storage for recent & bookmarked translations.

---

## 🔒 License & Security Note

Security configurations (HSTS, SSL Redirect, Secure Cookies) are enabled in `LanguageTranslator/settings/production.py`. Never commit your production `.env` file to public source control.
