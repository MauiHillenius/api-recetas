# Recipe API

## Project overview

REST API for managing recipes built with FastAPI and SQLite.

## Backend stack

- Python + FastAPI
- SQLModel + SQLite
- Uvicorn

## Project structure

- `main.py` — main application file with all endpoints and models
- `recipes.db` — SQLite database (auto-generated)
- `venv/` — virtual environment (do not modify)

## Commands

- Start server: `uvicorn main:app --reload`
- Install dependencies: `pip install fastapi uvicorn sqlmodel`

## Models

- `RecipeBase` — shared fields
- `Recipe` — database table
- `RecipeCreate` — POST body (no id)
- `RecipeUpdate` — PATCH body (all fields optional)
- `RecipeResponse` — response shape

## API endpoints

- `GET /recipes` — list all recipes
- `GET /recipes/{id}` — get recipe by id
- `POST /recipes` — create recipe
- `PUT /recipes/{id}` — full update
- `PATCH /recipes/{id}` — partial update
- `DELETE /recipes/{id}` — delete recipe

## Conventions

- English for all code, variables and comments
- HTTP exceptions for all errors (never return error dicts)
