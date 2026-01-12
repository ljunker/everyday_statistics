# Contributing to Everyday Statistics Service

Thanks for your interest in contributing!

---

## What this project does

This is a simple, self-hosted service for tracking everyday events (like pooping, coffee, walks) using Flask, SQLite, and Docker Compose.  
It has API key authentication, a web dashboard, backups, user management, and more.

---

## How to get started

1. **Fork this repo** and clone your fork locally.
2. Create a new branch for your changes:
   ```bash
   git checkout -b my-feature-branch
   ```

3. **Run it locally**:
   ```bash
   docker-compose up --build
   ```
   Use the `.env` file to set your API key and DB credentials.

4. Make your changes!

5. **Write clear commit messages.**

6. Push to your fork and open a **pull request**.  
   Describe what your change does and why it’s useful.

---

## What’s welcome

- Fix bugs
- Add new stats, insights, or charts
- Improve the frontend (UI/UX)
- Add more endpoints or filters
- Polish docs
- Help with tests

---

## Code style

- Keep it simple and readable.
- Use existing Python, Flask, and SQLAlchemy patterns.
- Add comments if something’s not obvious.

---

## Security

If you find a security issue (e.g., API key handling, auth bugs), **please report it privately** first instead of opening a public issue.

---

## Code of conduct

Be respectful, constructive, and collaborative.  
No poop jokes that cross the line.

---

Thanks for helping make Everyday Statistics better!
