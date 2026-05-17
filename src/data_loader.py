from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import (
    PROCESSED_FILES,
    RAW_CAUSES_FILE,
    RAW_DEATHS_FILE,
    RAW_DIVIPOLA_FILE,
    RAW_GEOJSON_FILE,
    REQUIRED_DEATH_COLUMNS,
)
from src.processing import build_cause_lookup, normalize_text_key


@dataclass
class DashboardBundle:
    ready: bool
    message: str
    deaths_by_department: pd.DataFrame | None = None
    deaths_by_month: pd.DataFrame | None = None
    top_violent_cities_x95: pd.DataFrame | None = None
    lowest_mortality_cities: pd.DataFrame | None = None
    top_causes: pd.DataFrame | None = None
    deaths_by_sex_department: pd.DataFrame | None = None
    deaths_by_age_group: pd.DataFrame | None = None
    kpis: dict[str, Any] | None = None
    geojson: dict[str, Any] | None = None


def source_files_exist() -> bool:
    return all(
        path.exists()
        for path in [
            RAW_DEATHS_FILE,
            RAW_CAUSES_FILE,
            RAW_DIVIPOLA_FILE,
            RAW_GEOJSON_FILE,
        ]
    )


def processed_files_exist() -> bool:
    return all(path.exists() for path in PROCESSED_FILES.values())


def read_excel_str(path: Path, **kwargs: Any) -> pd.DataFrame:
    return pd.read_excel(path, dtype=str, engine="openpyxl", **kwargs)


def load_deaths_raw() -> pd.DataFrame:
    df = read_excel_str(RAW_DEATHS_FILE)
    missing = [column for column in REQUIRED_DEATH_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"El archivo de mortalidad no contiene las columnas requeridas: {missing}")
    return df


def _find_header_row(df_preview: pd.DataFrame) -> int:
    for idx in range(min(len(df_preview), 25)):
        row = [normalize_text_key(value) for value in df_preview.iloc[idx].tolist()]
        if any("CODIGO" in cell and "CARACTER" in cell for cell in row) and any("DESCRIPCION" in cell for cell in row):
            return idx
    return 0


def _read_sheet_with_detected_header(path: Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path, engine="openpyxl")
    best: pd.DataFrame | None = None
    best_score = -1
    for sheet in xl.sheet_names:
        preview = pd.read_excel(path, sheet_name=sheet, header=None, dtype=str, engine="openpyxl", nrows=25)
        header_row = _find_header_row(preview)
        candidate = pd.read_excel(path, sheet_name=sheet, header=header_row, dtype=str, engine="openpyxl")
        candidate.columns = [str(col).strip() for col in candidate.columns]
        score = sum(
            1
            for column in candidate.columns
            if normalize_text_key(column) in {"COD_DANE", "COD_DEPARTAMENTO", "DEPARTAMENTO", "COD_MUNICIPIO", "MUNICIPIO"}
        )
        if score > best_score:
            best = candidate
            best_score = score
    if best is None:
        raise ValueError(f"No se pudo detectar una tabla válida en {path.name}.")
    return best


def load_divipola() -> pd.DataFrame:
    return _read_sheet_with_detected_header(RAW_DIVIPOLA_FILE)


def load_cause_dictionary() -> pd.DataFrame:
    xl = pd.ExcelFile(RAW_CAUSES_FILE, engine="openpyxl")
    if not xl.sheet_names:
        raise ValueError("El diccionario de causas no tiene hojas legibles.")

    preview = pd.read_excel(RAW_CAUSES_FILE, sheet_name=xl.sheet_names[0], header=None, dtype=str, engine="openpyxl", nrows=30)
    header_row = _find_header_row(preview)
    df = pd.read_excel(RAW_CAUSES_FILE, sheet_name=xl.sheet_names[0], header=header_row, dtype=str, engine="openpyxl")
    df.columns = [str(col).strip() for col in df.columns]
    return build_cause_lookup(df)


def load_geojson() -> dict[str, Any]:
    with open(RAW_GEOJSON_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def load_processed_csv(key: str) -> pd.DataFrame:
    path = PROCESSED_FILES[key]
    if not path.exists():
        raise FileNotFoundError(f"Falta el archivo procesado: {path}")
    df = pd.read_csv(path, dtype=str)
    for numeric_column in ["TOTAL", "ORDEN_EDAD"]:
        if numeric_column in df.columns:
            df[numeric_column] = pd.to_numeric(df[numeric_column], errors="coerce").fillna(0).astype("int64")
    return df


def load_processed_kpis() -> dict[str, Any]:
    path = PROCESSED_FILES["kpis"]
    if not path.exists():
        raise FileNotFoundError(f"Falta el archivo procesado: {path}")
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def missing_processed_files() -> list[str]:
    return [str(path) for path in PROCESSED_FILES.values() if not path.exists()]


def load_dashboard_bundle() -> DashboardBundle:
    missing = missing_processed_files()
    if missing:
        return DashboardBundle(
            ready=False,
            message=(
                "Faltan archivos procesados en data/processed. Ejecuta:\n\n"
                "python scripts/prepare_data.py\n\n"
                "Archivos faltantes:\n- " + "\n- ".join(missing)
            ),
        )

    try:
        return DashboardBundle(
            ready=True,
            message="Datos procesados cargados correctamente.",
            deaths_by_department=load_processed_csv("deaths_by_department"),
            deaths_by_month=load_processed_csv("deaths_by_month"),
            top_violent_cities_x95=load_processed_csv("top_violent_cities_x95"),
            lowest_mortality_cities=load_processed_csv("lowest_mortality_cities"),
            top_causes=load_processed_csv("top_causes"),
            deaths_by_sex_department=load_processed_csv("deaths_by_sex_department"),
            deaths_by_age_group=load_processed_csv("deaths_by_age_group"),
            kpis=load_processed_kpis(),
            geojson=load_geojson(),
        )
    except Exception as exc:  # pragma: no cover - fallback de usuario
        return DashboardBundle(
            ready=False,
            message=(
                "No fue posible cargar los archivos procesados. "
                "Ejecuta nuevamente:\n\npython scripts/prepare_data.py\n\n"
                f"Detalle técnico: {exc}"
            ),
        )
