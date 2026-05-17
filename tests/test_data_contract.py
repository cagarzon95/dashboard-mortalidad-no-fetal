from __future__ import annotations

import json

import pandas as pd
import pytest

from src.config import (
    PROCESSED_FILES,
    RAW_CAUSES_FILE,
    RAW_DEATHS_FILE,
    RAW_DIVIPOLA_FILE,
    RAW_GEOJSON_FILE,
)
from src.data_loader import load_cause_dictionary, load_deaths_raw, load_divipola, load_geojson
from src.processing import build_monthly_deaths, build_top_causes, prepare_deaths_dataframe


@pytest.fixture(scope="session", autouse=True)
def ensure_processed_data():
    missing = [path for path in PROCESSED_FILES.values() if not path.exists()]
    if missing:
        import subprocess
        import sys

        subprocess.run([sys.executable, "scripts/prepare_data.py"], check=True)


@pytest.fixture(scope="session")
def raw_deaths():
    return load_deaths_raw()


@pytest.fixture(scope="session")
def prepared_deaths(raw_deaths):
    return prepare_deaths_dataframe(raw_deaths)


@pytest.fixture(scope="session")
def cause_lookup():
    return load_cause_dictionary()


@pytest.fixture(scope="session")
def divipola():
    return load_divipola()


@pytest.fixture(scope="session")
def geojson():
    return load_geojson()


def test_source_files_exist():
    assert RAW_DEATHS_FILE.exists()
    assert RAW_CAUSES_FILE.exists()
    assert RAW_DIVIPOLA_FILE.exists()
    assert RAW_GEOJSON_FILE.exists()


def test_mortality_loads_as_text():
    df = load_deaths_raw()
    for column in ["COD_DEPARTAMENTO", "COD_DANE", "COD_MUERTE", "MES", "SEXO", "GRUPO_EDAD1"]:
        assert column in df.columns
        assert pd.api.types.is_string_dtype(df[column]) or df[column].dtype == object


def test_department_code_keeps_two_digits(prepared_deaths):
    df = prepared_deaths
    non_empty = df["COD_DEPARTAMENTO"].dropna().astype(str)
    assert non_empty.str.len().min() >= 2
    assert non_empty.str.len().max() == 2


def test_geojson_contains_dpto(geojson):
    assert "features" in geojson
    assert geojson["features"]
    assert "DPTO" in geojson["features"][0]["properties"]


def test_monthly_aggregation_uses_valid_months(prepared_deaths):
    deaths = prepared_deaths
    monthly = build_monthly_deaths(deaths)
    assert set(monthly["MES"]).issubset({f"{i:02d}" for i in range(1, 13)})
    assert monthly["TOTAL"].ge(0).all()


def test_x95_filter_startswith(prepared_deaths):
    deaths = prepared_deaths
    x95 = deaths.loc[deaths["COD_MUERTE"].str.startswith("X95", na=False)]
    assert len(x95) > 0
    assert x95["COD_MUERTE"].str.startswith("X95", na=False).all()


def test_top_causes_have_descriptions(prepared_deaths, cause_lookup):
    deaths = prepared_deaths
    top_causes = build_top_causes(deaths, cause_lookup)
    assert "CAUSA_DE_MUERTE" in top_causes.columns
    assert top_causes["CAUSA_DE_MUERTE"].notna().all()
    assert (top_causes["CAUSA_DE_MUERTE"] != top_causes["COD_MUERTE"]).any()


def test_processed_files_created():
    for path in PROCESSED_FILES.values():
        assert path.exists()
