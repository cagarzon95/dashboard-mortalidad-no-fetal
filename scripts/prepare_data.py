from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROCESSED_DIR, PROCESSED_FILES  # noqa: E402
from src.data_loader import load_cause_dictionary, load_deaths_raw, load_divipola, load_geojson  # noqa: E402
from src.processing import (  # noqa: E402
    build_age_group,
    build_department_deaths,
    build_divipola_lookups,
    build_kpis,
    build_lowest_mortality_cities,
    build_monthly_deaths,
    build_sex_department,
    build_top_causes,
    build_violent_cities_x95,
    prepare_deaths_dataframe,
)


def ensure_output_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ensure_output_dir()

    deaths_raw = load_deaths_raw()
    divipola_raw = load_divipola()
    cause_lookup = load_cause_dictionary()
    geojson = load_geojson()

    deaths = prepare_deaths_dataframe(deaths_raw)
    dept_lookup, muni_lookup = build_divipola_lookups(divipola_raw)

    deaths_by_department = build_department_deaths(deaths, dept_lookup)
    deaths_by_month = build_monthly_deaths(deaths)
    top_violent_cities_x95 = build_violent_cities_x95(deaths, muni_lookup, dept_lookup)
    lowest_mortality_cities = build_lowest_mortality_cities(deaths, muni_lookup, dept_lookup)
    top_causes = build_top_causes(deaths, cause_lookup)
    deaths_by_sex_department = build_sex_department(deaths, dept_lookup)
    deaths_by_age_group = build_age_group(deaths)
    kpis = build_kpis(
        deaths,
        deaths_by_department,
        deaths_by_month,
        top_causes,
        top_violent_cities_x95,
    )

    deaths_by_department.to_csv(PROCESSED_FILES["deaths_by_department"], index=False, encoding="utf-8")
    deaths_by_month.to_csv(PROCESSED_FILES["deaths_by_month"], index=False, encoding="utf-8")
    top_violent_cities_x95.to_csv(PROCESSED_FILES["top_violent_cities_x95"], index=False, encoding="utf-8")
    lowest_mortality_cities.to_csv(PROCESSED_FILES["lowest_mortality_cities"], index=False, encoding="utf-8")
    top_causes.to_csv(PROCESSED_FILES["top_causes"], index=False, encoding="utf-8")
    deaths_by_sex_department.to_csv(PROCESSED_FILES["deaths_by_sex_department"], index=False, encoding="utf-8")
    deaths_by_age_group.to_csv(PROCESSED_FILES["deaths_by_age_group"], index=False, encoding="utf-8")
    with open(PROCESSED_FILES["kpis"], "w", encoding="utf-8") as handle:
        json.dump(kpis, handle, ensure_ascii=False, indent=2)

    total_records = len(deaths)
    n_departments = deaths["COD_DEPARTAMENTO"].nunique(dropna=True)
    n_municipalities = deaths["COD_DANE"].nunique(dropna=True)
    n_death_codes = deaths["COD_MUERTE"].nunique(dropna=True)
    n_x95 = int(deaths["COD_MUERTE"].str.startswith("X95", na=False).sum())

    print("Resumen de preparación")
    print(f"Registros leídos: {total_records:,}".replace(",", "."))
    print(f"Departamentos únicos: {n_departments:,}".replace(",", "."))
    print(f"Municipios únicos: {n_municipalities:,}".replace(",", "."))
    print(f"Códigos de muerte únicos: {n_death_codes:,}".replace(",", "."))
    print(f"Registros X95: {n_x95:,}".replace(",", "."))
    print("Archivos generados:")
    for name, path in PROCESSED_FILES.items():
        print(f"- {name}: {path}")
    print(f"GeoJSON cargado: {len(geojson.get('features', []))} departamentos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
