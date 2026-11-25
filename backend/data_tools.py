"""Import, manage, summarize and export TTFIT data from JSON or CSV files."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from main import db, init


FOOD_FIELDS = (
    "name",
    "calories_100g",
    "protein_100g",
    "carbs_100g",
    "fat_100g",
)
ENTRY_FIELDS = (
    "id",
    "food_id",
    "food_name",
    "grams",
    "calories",
    "protein_g",
    "carbs_g",
    "fat_g",
    "entry_date",
)


def validate_food(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one food dictionary before it reaches SQLite."""
    if not isinstance(record, dict):
        raise ValueError("Cada alimento deve ser um objeto/dicionário.")

    name = str(record.get("name", "")).strip()
    if not name or len(name) > 120:
        raise ValueError("O nome deve ter entre 1 e 120 caracteres.")

    clean: dict[str, Any] = {"name": name}
    for field in FOOD_FIELDS[1:]:
        try:
            value = float(record[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"'{field}' deve ser um número válido.") from exc
        if not math.isfinite(value) or value < 0 or value > 100000:
            raise ValueError(f"'{field}' deve estar entre 0 e 100000.")
        clean[field] = value
    return clean


def read_records(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSON array/object or a CSV table as a list of dictionaries."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".json":
        with source.open("r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
        if isinstance(data, dict):
            data = data.get("foods", data.get("entries", [data]))
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise ValueError("O JSON deve conter uma lista de objetos.")
        return data
    if suffix == ".csv":
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    raise ValueError("Formato não suportado. Use arquivos .json ou .csv.")


def write_records(path: str | Path, records: Iterable[dict[str, Any]], fields: tuple[str, ...]) -> int:
    """Write dictionaries to JSON or CSV and return the number of rows written."""
    destination = Path(path)
    rows = [{field: row.get(field) for field in fields} for row in records]
    if destination.suffix.lower() == ".json":
        with destination.open("w", encoding="utf-8", newline="") as stream:
            json.dump(rows, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    elif destination.suffix.lower() == ".csv":
        with destination.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError("Formato não suportado. Use uma extensão .json ou .csv.")
    return len(rows)


def add_food(record: dict[str, Any]) -> dict[str, Any]:
    """Validate and register one food in the TTFIT database."""
    init()
    food = validate_food(record)
    try:
        with db() as connection:
            cursor = connection.execute(
                "INSERT INTO foods(name, calories_100g, protein_100g, carbs_100g, fat_100g) "
                "VALUES(?, ?, ?, ?, ?)",
                tuple(food[field] for field in FOOD_FIELDS),
            )
            food["id"] = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError(f"O alimento '{food['name']}' já está cadastrado.") from exc
    return food


def import_foods(path: str | Path) -> int:
    """Validate and insert all foods from a CSV/JSON file atomically."""
    init()
    foods = [validate_food(row) for row in read_records(path)]
    if not foods:
        raise ValueError("O arquivo não contém alimentos.")
    with db() as connection:
        try:
            connection.executemany(
                "INSERT INTO foods(name, calories_100g, protein_100g, carbs_100g, fat_100g) "
                "VALUES(:name, :calories_100g, :protein_100g, :carbs_100g, :fat_100g)",
                foods,
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(
                "Importação cancelada: há alimento repetido no arquivo ou já cadastrado no sistema."
            ) from exc
    return len(foods)


def list_foods() -> list[dict[str, Any]]:
    """Return foods ordered alphabetically as dictionaries."""
    init()
    with db() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM foods ORDER BY name")]


def search_foods(term: str) -> list[dict[str, Any]]:
    """Search food names without case sensitivity."""
    query = term.strip().casefold()
    if not query:
        raise ValueError("Informe um termo para a busca.")
    return [food for food in list_foods() if query in food["name"].casefold()]


def list_entries(day: date | None = None) -> list[dict[str, Any]]:
    """Return meal diary records for a day, newest first."""
    init()
    target_day = (day or date.today()).isoformat()
    query = (
        "SELECT e.id, e.food_id, f.name AS food_name, e.grams, e.entry_date, "
        "f.calories_100g, f.protein_100g, f.carbs_100g, f.fat_100g "
        "FROM entries e JOIN foods f ON f.id=e.food_id "
        "WHERE e.entry_date=? ORDER BY e.id DESC"
    )
    with db() as connection:
        rows = connection.execute(query, (target_day,)).fetchall()
    result = []
    for row in rows:
        scale = row["grams"] / 100
        result.append(
            {
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
        )
    return result


def calculate_totals(entries: Iterable[dict[str, Any]]) -> dict[str, float]:
    """Calculate calories and macros from a list of diary-entry dictionaries."""
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for entry in entries:
        for field in totals:
            try:
                value = float(entry[field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"Registro inválido: campo '{field}' ausente ou não numérico.") from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Registro inválido: '{field}' deve ser um número não negativo.")
            totals[field] += value
    return {field: round(value, 2) for field, value in totals.items()}


def export_foods(path: str | Path) -> int:
    """Export the food catalog to JSON or CSV."""
    return write_records(path, list_foods(), ("id",) + FOOD_FIELDS)


def export_entries(path: str | Path, day: date | None = None) -> int:
    """Export one day's diary to JSON or CSV."""
    return write_records(path, list_entries(day), ENTRY_FIELDS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ferramentas de dados do TTFIT (JSON/CSV e SQLite).")
    commands = parser.add_subparsers(dest="command", required=True)

    imp = commands.add_parser("import-foods", help="Importar alimentos de um arquivo JSON ou CSV.")
    imp.add_argument("arquivo", type=Path)

    add = commands.add_parser("add-food", help="Cadastrar um alimento no banco do TTFIT.")
    add.add_argument("nome")
    for field, label in (("calories_100g", "calorias"), ("protein_100g", "proteina"),
                         ("carbs_100g", "carboidratos"), ("fat_100g", "gordura")):
        add.add_argument(f"--{label}", dest=field, type=float, required=True)

    commands.add_parser("list-foods", help="Listar alimentos cadastrados.")
    search = commands.add_parser("search", help="Buscar alimentos pelo nome.")
    search.add_argument("termo")

    exp_foods = commands.add_parser("export-foods", help="Exportar o catálogo em JSON ou CSV.")
    exp_foods.add_argument("arquivo", type=Path)
    exp_entries = commands.add_parser("export-entries", help="Exportar o diário de hoje em JSON ou CSV.")
    exp_entries.add_argument("arquivo", type=Path)

    summary = commands.add_parser("summary", help="Calcular os totais nutricionais do dia.")
    summary.add_argument("--date", type=date.fromisoformat, default=date.today())
    return parser


def run(args: argparse.Namespace) -> int:
    """Execute one CLI operation and print a concise result."""
    init()
    if args.command == "import-foods":
        print(f"Alimentos importados: {import_foods(args.arquivo)}")
    elif args.command == "add-food":
        food = add_food({"name": args.nome, **{field: getattr(args, field) for field in FOOD_FIELDS[1:]}})
        print(f"Alimento cadastrado (ID {food['id']}): {food['name']}")
    elif args.command == "list-foods":
        print(json.dumps(list_foods(), ensure_ascii=False, indent=2))
    elif args.command == "search":
        print(json.dumps(search_foods(args.termo), ensure_ascii=False, indent=2))
    elif args.command == "export-foods":
        print(f"Alimentos exportados: {export_foods(args.arquivo)}")
    elif args.command == "export-entries":
        print(f"Registros exportados: {export_entries(args.arquivo)}")
    elif args.command == "summary":
        print(json.dumps(calculate_totals(list_entries(args.date)), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    try:
        return run(build_parser().parse_args())
    except (OSError, sqlite3.Error, ValueError, json.JSONDecodeError, csv.Error) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
