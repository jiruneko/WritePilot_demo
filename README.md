# WritePilot Demo

**WritePilot** is a live demo application showcasing an AI-powered English writing workflow built with **FastAPI** and **OpenAI**.

This project demonstrates how to design, implement, and deploy a minimal yet production-style AI CMS, including both a REST API and a Web UI.

🌐 **Live Demo**  
- Web UI: https://writepilot-demo.onrender.com/ui  
- API Docs (Swagger): https://writepilot-demo.onrender.com/docs

---

## Features

- ✍️ Generate English blog articles using OpenAI
- 🎯 Rewrite articles by tone (e.g. friendly, professional, confident)
- 🗄 Persist articles to a database (SQLite)
- 🔄 Full CRUD operations (Create, Read, Update, Delete)
- 🌍 Web UI + REST API
- 🚀 Deployed to the cloud (Render)

---

## Tech Stack

- **Backend**: FastAPI
- **LLM**: OpenAI API
- **Database**: SQLite (demo purpose)
- **ORM**: SQLAlchemy
- **Templates**: Jinja2
- **Deployment**: Render
- **Environment Management**: python-dotenv

---

## Project Structure

```text
app/
├── api/            # REST API routes
├── ui/             # Web UI routes
├── services/       # OpenAI client logic
├── db/             # Database models & session
├── templates/      # Jinja2 templates
├── main.py         # Application entry point
