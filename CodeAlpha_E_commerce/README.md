# CA-Tech Electronics

Production-minded Django ecommerce application for electronics retail. It includes reusable apps for accounts, products, cart, orders, core pages, and a staff dashboard.

## Features

- Register, login, logout, password reset, profile, and edit profile
- Product categories, brands, images, variants, details, related products, search, filters, sorting, and pagination
- Persistent cart for anonymous sessions and authenticated users
- Checkout with billing, shipping, cash on delivery, tax, shipping calculation, and confirmation
- Order history and status tracking
- Staff dashboard with revenue, orders, users, products, status analytics, and low-stock monitoring
- Premium responsive UI with glassmorphism, dark mode, Swiper hero, AOS scroll reveal, GSAP entrance animation, ripple buttons, image zoom, loading screen, skeleton shimmer, and animated cart feedback

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_sample_data
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.//or run the bat file first than open this address in browser

Sample staff account:

- Username: `codealpha`
- Password: `code1234`

Change the sample password and `DJANGO_SECRET_KEY` before deployment.

## Deployment Notes

- Set `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to the production hostnames.
- Use a strong `DJANGO_SECRET_KEY`.
- Run `python manage.py collectstatic`.
- Use HTTPS and configure secure cookie settings at the hosting layer.
- SQLite is included per project requirements. For higher traffic stores, migrate to PostgreSQL.
