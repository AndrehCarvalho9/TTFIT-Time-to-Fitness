from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

import auth_store


ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB = Path(__file__).resolve().parent / "ttfit.db"
app = FastAPI(title="TTFIT API", description="API de alimentação e perfil do TTFIT.", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("TTFIT_SESSION_SECRET") or secrets.token_urlsafe(32),
    session_cookie="ttfit_session",
    same_site="lax",
    https_only=os.getenv("TTFIT_HTTPS_ONLY", "false").lower() == "true",
)

SEED = [
    ("Arroz cozido", 130, 2.7, 28.2, 0.3),
    ("Feijão cozido", 76, 4.8, 13.6, 0.5),
    ("Peito de frango grelhado", 165, 31, 0, 3.6),
    ("Ovo cozido", 155, 13, 1.1, 11),
    ("Banana", 89, 1.1, 22.8, 0.3),
    ("Aveia", 389, 16.9, 66.3, 6.9),
]


def db():
    connection = sqlite3.connect(DB)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def init() -> None:
    with db() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS foods ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, "
            "calories_100g REAL NOT NULL, protein_100g REAL NOT NULL, "
            "carbs_100g REAL NOT NULL, fat_100g REAL NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, food_id INTEGER NOT NULL, "
            "grams REAL NOT NULL CHECK(grams>0), entry_date TEXT NOT NULL, "
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP, "
            "FOREIGN KEY(food_id) REFERENCES foods(id))"
        )
        if connection.execute("SELECT COUNT(*) FROM foods").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO foods(name, calories_100g, protein_100g, carbs_100g, fat_100g) "
                "VALUES(?, ?, ?, ?, ?)",
                SEED,
            )
    auth_store.init_auth_store()


@app.on_event("startup")
def startup() -> None:
    init()


class NewEntry(BaseModel):
    food_id: int
    grams: float = Field(gt=0, le=3000)


class RegisterPayload(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginPayload(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class ProfilePayload(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    age: int | None = Field(default=None, ge=13, le=120)
    height_cm: float | None = Field(default=None, ge=80, le=250)
    weight_kg: float | None = Field(default=None, ge=25, le=350)
    goal: str | None = Field(default=None, max_length=240)


def serialize(row):
    scale = row["grams"] / 100
    return {
        "id": row["id"],
        "food_id": row["food_id"],
        "food_name": row["food_name"],
        "grams": row["grams"],
        "calories": round(row["calories_100g"] * scale, 2),
        "protein_g": round(row["protein_100g"] * scale, 2),
        "carbs_g": round(row["carbs_100g"] * scale, 2),
        "fat_g": round(row["fat_100g"] * scale, 2),
        "entry_date": row["entry_date"],
    }


QUERY = (
    "SELECT e.id, e.food_id, e.grams, e.entry_date, f.name AS food_name, "
    "f.calories_100g, f.protein_100g, f.carbs_100g, f.fat_100g "
    "FROM entries e JOIN foods f ON f.id=e.food_id"
)
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PASSWORD_ITERATIONS = 310_000


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise HTTPException(422, "Informe um e-mail válido.")
    return email


def password_hash(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def password_matches(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def current_user(request: Request) -> dict:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(401, "Entre na sua conta para continuar.")
    try:
        user = auth_store.public_user(auth_store.get_user_by_id(int(user_id)))
    except Exception as exc:
        raise HTTPException(503, "Não foi possível acessar o banco de dados.") from exc
    if user is None:
        request.session.clear()
        raise HTTPException(401, "Sua sessão expirou. Entre novamente.")
    return user


@app.get("/")
def root():
    return {"app": "TTFIT API", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/foods")
def foods():
    with db() as connection:
        rows = connection.execute("SELECT * FROM foods ORDER BY name").fetchall()
    return [dict(row) for row in rows]


@app.get("/api/entries")
def get_entries():
    with db() as connection:
        rows = connection.execute(
            QUERY + " WHERE e.entry_date=? ORDER BY e.id DESC", (date.today().isoformat(),)
        ).fetchall()
    return [serialize(row) for row in rows]


@app.post("/api/entries", status_code=201)
def add_entry(payload: NewEntry):
    with db() as connection:
        if not connection.execute("SELECT id FROM foods WHERE id=?", (payload.food_id,)).fetchone():
            raise HTTPException(404, "Alimento não encontrado.")
        cursor = connection.execute(
            "INSERT INTO entries(food_id, grams, entry_date) VALUES(?, ?, ?)",
            (payload.food_id, payload.grams, date.today().isoformat()),
        )
        row = connection.execute(QUERY + " WHERE e.id=?", (cursor.lastrowid,)).fetchone()
    return serialize(row)


@app.delete("/api/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int):
    with db() as connection:
        cursor = connection.execute(
            "DELETE FROM entries WHERE id=? AND entry_date=?", (entry_id, date.today().isoformat())
        )
        if cursor.rowcount == 0:
            raise HTTPException(404, "Registro não encontrado.")


@app.delete("/api/entries", status_code=204)
def clear_entries():
    with db() as connection:
        connection.execute("DELETE FROM entries WHERE entry_date=?", (date.today().isoformat(),))


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterPayload, request: Request):
    name = payload.name.strip()
    if len(name) < 2:
        raise HTTPException(422, "Informe seu nome completo.")
    email = normalize_email(payload.email)
    try:
        user = auth_store.create_user(name, email, password_hash(payload.password))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(409, "Este e-mail já possui uma conta.") from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        if getattr(exc, "errno", None) == 1062:
            raise HTTPException(409, "Este e-mail já possui uma conta.") from exc
        raise HTTPException(503, "Não foi possível acessar o banco de dados.") from exc
    request.session["user_id"] = user["id"]
    return {"user": auth_store.public_user(user)}


@app.post("/api/auth/login")
def login(payload: LoginPayload, request: Request):
    email = normalize_email(payload.email)
    try:
        user = auth_store.get_user_by_email(email)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(503, "Não foi possível acessar o banco de dados.") from exc
    if user is None or not password_matches(payload.password, user["password_hash"]):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    request.session["user_id"] = user["id"]
    return {"user": auth_store.public_user(user)}


@app.get("/api/auth/me")
def get_profile(request: Request):
    return {"user": current_user(request)}


@app.put("/api/auth/me")
def update_profile(payload: ProfilePayload, request: Request):
    user = current_user(request)
    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"] is not None:
        updates["name"] = updates["name"].strip()
        if len(updates["name"]) < 2:
            raise HTTPException(422, "Informe pelo menos 2 caracteres no nome.")
    if "goal" in updates and updates["goal"] is not None:
        updates["goal"] = updates["goal"].strip()
    try:
        updated = auth_store.public_user(auth_store.update_user(user["id"], updates))
    except Exception as exc:
        raise HTTPException(503, "Não foi possível salvar seu perfil.") from exc
    return {"user": updated}


@app.post("/api/auth/logout", status_code=204)
def logout(request: Request):
    request.session.clear()


@app.delete("/api/auth/me", status_code=204)
def delete_account(request: Request):
    user = current_user(request)
    try:
        auth_store.delete_user(user["id"])
    except Exception as exc:
        raise HTTPException(503, "Não foi possível excluir sua conta.") from exc
    request.session.clear()
