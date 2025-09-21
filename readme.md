# 📚 Bookish

Bookish is a full-stack Flask web application that helps readers track their books, import data from Goodreads/StoryGraph, and discover new recommendations using the OpenLibrary API.

The app also integrates with external book sources (OpenLibrary, Google Books, Project Gutenberg) to suggest free or affordable deals, and runs background workers to process tasks like recommendations and CSV imports asynchronously.

---

![Bookish Homepage](docs/screenshots/index.jpg)

---
## Features

* **User Accounts**

  * Register, login, and manage your profile securely (Flask-Login + hashed passwords).
  * Update name, email, or password.

* **Book Tracking**
  * Upload your Goodreads or StoryGraph CSV exports.
  * Mark books as read, on your watchlist, or recommended.
* **Personalized Recommendations**
  * Analyzes your subjects and genres.
  * Fetches books from OpenLibrary in bulk.
  * Sorts, filters, and recommends new books just for you.
* **Book Deals**
  * Finds free editions from OpenLibrary / Gutenberg / Standard Ebooks.
  * Queries Google Books for deals and buy links.
  * Saves the best deal directly into your library.
* **Search**
  * Search OpenLibrary by title, author, or subject.
  * Save results directly to your watchlist or mark as read.
* **Background Processing**
  * Long-running tasks (like recommendations and CSV imports) run asynchronously via a worker service.
  * Keeps the UI responsive.

---

## 🛠️ Tech Stack

**Frontend**
* Jinja2 templates
* Bootstrap 5 Styling
**Backend**
* Flask (Python 3.12+)
* SQLAlchemy ORM + PostgreSQL (via Neon DB)
* Flask-Login for authentication
* Flask-WTF for forms
* aiohttp for async OpenLibrary calls
**Workers / Background Tasks**
* Cloud Function + Flask worker (deployed separately)
* Runs recommendation and CSV import jobs asynchronously

