from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DEATHS_FILE = DATA_DIR / "Anexo1.NoFetal2019_CE_15-03-23.xlsx"
RAW_CAUSES_FILE = DATA_DIR / "Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx"
RAW_DIVIPOLA_FILE = DATA_DIR / "Divipola_CE_.xlsx"
RAW_GEOJSON_FILE = DATA_DIR / "Colombia.geo.json"

PROCESSED_FILES = {
    "deaths_by_department": PROCESSED_DIR / "deaths_by_department.csv",
    "deaths_by_month": PROCESSED_DIR / "deaths_by_month.csv",
    "top_violent_cities_x95": PROCESSED_DIR / "top_violent_cities_x95.csv",
    "lowest_mortality_cities": PROCESSED_DIR / "lowest_mortality_cities.csv",
    "top_causes": PROCESSED_DIR / "top_causes.csv",
    "deaths_by_sex_department": PROCESSED_DIR / "deaths_by_sex_department.csv",
    "deaths_by_age_group": PROCESSED_DIR / "deaths_by_age_group.csv",
    "kpis": PROCESSED_DIR / "kpis.json",
}

REQUIRED_DEATH_COLUMNS = [
    "COD_DANE",
    "COD_DEPARTAMENTO",
    "COD_MUNICIPIO",
    "AREA_DEFUNCION",
    "SITIO_DEFUNCION",
    "AÑO",
    "MES",
    "HORA",
    "MINUTOS",
    "SEXO",
    "ESTADO_CIVIL",
    "GRUPO_EDAD1",
    "NIVEL_EDUCATIVO",
    "MANERA_MUERTE",
    "COD_MUERTE",
    "IDPROFESIONAL",
]

MONTH_ORDER = [f"{month:02d}" for month in range(1, 13)]
MONTH_LABELS_ES = {
    "01": "Enero",
    "02": "Febrero",
    "03": "Marzo",
    "04": "Abril",
    "05": "Mayo",
    "06": "Junio",
    "07": "Julio",
    "08": "Agosto",
    "09": "Septiembre",
    "10": "Octubre",
    "11": "Noviembre",
    "12": "Diciembre",
}

SEXO_LABELS = {
    "1": "Hombre",
    "2": "Mujer",
    "3": "Indeterminado",
}

AGE_GROUP_DEFINITIONS = [
    {"codes": [0, 1, 2, 3, 4], "label": "Mortalidad neonatal", "range": "Menor de 1 mes"},
    {"codes": [5, 6], "label": "Mortalidad infantil", "range": "1 a 11 meses"},
    {"codes": [7, 8], "label": "Primera infancia", "range": "1 a 4 años"},
    {"codes": [9, 10], "label": "Niñez", "range": "5 a 14 años"},
    {"codes": [11], "label": "Adolescencia", "range": "15 a 19 años"},
    {"codes": [12, 13], "label": "Juventud", "range": "20 a 29 años"},
    {"codes": [14, 15, 16], "label": "Adultez temprana", "range": "30 a 44 años"},
    {"codes": [17, 18, 19], "label": "Adultez intermedia", "range": "45 a 59 años"},
    {"codes": [20, 21, 22, 23, 24], "label": "Vejez", "range": "60 a 84 años"},
    {
        "codes": [25, 26, 27, 28],
        "label": "Longevidad / Centenarios",
        "range": "85 a 100+ años",
    },
    {"codes": [29], "label": "Edad desconocida", "range": "Sin información"},
]

AGE_GROUP_ORDER = [item["label"] for item in AGE_GROUP_DEFINITIONS] + ["Sin información"]

