"""User account storage for SQLite development and optional MySQL hosting."""

from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


SQLITE_DB = Path(__file__).resolve().parent / "ttfit.db"
USER_FIELDS = {"name", "age", "height_cm", "weight_kg", "goal"}
USER_COLUMNS = "id, name, email, password_hash, age, height_cm, weight_kg, goal, created_at"


def mysql_settings() -> dict[str, Any] | None:
    """Return complete MySQL settings, None when no MySQL config was supplied."""
    keys = {
        "host": "MYSQL_HOST",
        "user": "MYSQL_USER",
        "password": "MYSQL_PASSWORD",
        "database": "MYSQL_DATABASE",
    }
    values = {field: os.getenv(key, "").strip() for field, key in keys.items()}
    if not any(values.values()):
        return None
    missing = [key for field, key in keys.items() if not values[field]]
    if missing:
        raise RuntimeError("Configuração MySQL incompleta. Preencha: " + ", ".join(missing))
    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("MYSQL_PORT deve ser numérica.") from exc
    return {**values, "port": port, "connection_timeout": 8}


def database_label() -> str:
    return "MySQL" if mysql_settings() else "SQLite local"


def _connect() -> tuple[Any, bool]:
    settings = mysql_settings()
    if settings:
        try:
            import mysql.connector
        except ImportError as exc:
            raise RuntimeError("Dependência mysql-connector-python ausente.") from exc
        return mysql.connector.connect(**settings), True
    connection = sqlite3.connect(SQLITE_DB)
    connection.row_factory = sqlite3.Row
    return connection, False


def _cursor(connection: Any, is_mysql: bool) -> Any:
    return connection.cursor(dictionary=True) if is_mysql else connection.cursor()


def _sql(query: str, is_mysql: bool) -> str:
    return query.replace("?", "%s") if is_mysql else query


def init_auth_store() -> None:
    """Create the account table in the selected database if it does not exist."""
    connection, is_mysql = _connect()
    cursor = _cursor(connection, is_mysql)
    if is_mysql:
        statement = """CREATE TABLE IF NOT EXISTS g01_users (
            id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(80) NOT NULL,
            email VARCHAR(254) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            age SMALLINT UNSIGNED NULL,
            height_cm DECIMAL(5,2) NULL,
            weight_kg DECIMAL(6,2) NULL,
            goal VARCHAR(240) NOT NULL DEFAULT '',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
    else:
        statement = """CREATE TABLE IF NOT EXISTS g01_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            age INTEGER NULL,
            height_cm REAL NULL,
            weight_kg REAL NULL,
            goal TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    try:
        cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def _to_public_user(row: Any) -> dict[str, Any] | None:
    if row is None:
        return None
    result = dict(row)
    result.pop("password_hash", None)
    for key, value in result.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
    return result


def _fetch_one(query: str, params: tuple[Any, ...]) -> dict[str, Any] | None:
    connection, is_mysql = _connect()
    cursor = _cursor(connection, is_mysql)
    try:
        cursor.execute(_sql(query, is_mysql), params)
        return cursor.fetchone()
    finally:
        cursor.close()
        connection.close()


def get_user_by_email(email: str) -> dict[str, Any] | None:
    return _fetch_one(f"SELECT {USER_COLUMNS} FROM g01_users WHERE email=?", (email,))


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    return _fetch_one(f"SELECT {USER_COLUMNS} FROM g01_users WHERE id=?", (user_id,))


def create_user(name: str, email: str, password_hash: str) -> dict[str, Any]:
    connection, is_mysql = _connect()
    cursor = _cursor(connection, is_mysql)
    try:
        cursor.execute(
            _sql("INSERT INTO g01_users(name, email, password_hash) VALUES(?, ?, ?)", is_mysql),
            (name, email, password_hash),
        )
        user_id = cursor.lastrowid
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    return get_user_by_id(int(user_id)) or {}


def update_user(user_id: int, updates: dict[str, Any]) -> dict[str, Any] | None:
    fields = [(key, value) for key, value in updates.items() if key in USER_FIELDS]
    if not fields:
        return get_user_by_id(user_id)
    assignments = ", ".join(f"{key}=?" for key, _ in fields)
    connection, is_mysql = _connect()
    cursor = _cursor(connection, is_mysql)
    try:
        cursor.execute(
            _sql(f"UPDATE g01_users SET {assignments} WHERE id=?", is_mysql),
            tuple(value for _, value in fields) + (user_id,),
        )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    return get_user_by_id(user_id)


def delete_user(user_id: int) -> bool:
    connection, is_mysql = _connect()
    cursor = _cursor(connection, is_mysql)
    try:
        cursor.execute(_sql("DELETE FROM g01_users WHERE id=?", is_mysql), (user_id,))
        deleted = cursor.rowcount > 0
        connection.commit()
        return deleted
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def public_user(row: dict[str, Any] | None) -> dict[str, Any] | None:
    return _to_public_user(row)
