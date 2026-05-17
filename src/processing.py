from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from src.config import AGE_GROUP_DEFINITIONS, AGE_GROUP_ORDER, MONTH_LABELS_ES, MONTH_ORDER, SEXO_LABELS


def normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def normalize_text_key(value: object) -> str:
    text = normalize_text(value).upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("\n", " ").replace("\r", " ")
    return " ".join(text.split())


def normalize_numeric_code(series: pd.Series, width: int) -> pd.Series:
    def _normalize(value: object) -> str:
        text = normalize_text(value)
        if not text:
            return ""
        if text.endswith(".0"):
            text = text[:-2]
        text = text.strip()
        if text.isdigit():
            return text.zfill(width)
        return text

    return series.map(_normalize).astype("string")


def normalize_alphanumeric_code(series: pd.Series) -> pd.Series:
    def _normalize(value: object) -> str:
        text = normalize_text(value)
        if not text:
            return ""
        if text.endswith(".0"):
            text = text[:-2]
        return text.strip().upper()

    return series.map(_normalize).astype("string")


def normalize_month_code(series: pd.Series) -> pd.Series:
    month_names = {
        "ENERO": "01",
        "FEBRERO": "02",
        "MARZO": "03",
        "ABRIL": "04",
        "MAYO": "05",
        "JUNIO": "06",
        "JULIO": "07",
        "AGOSTO": "08",
        "SEPTIEMBRE": "09",
        "SETIEMBRE": "09",
        "OCTUBRE": "10",
        "NOVIEMBRE": "11",
        "DICIEMBRE": "12",
    }

    def _normalize(value: object) -> str:
        text = normalize_text(value)
        if not text:
            return ""
        if text.endswith(".0"):
            text = text[:-2]
        upper = normalize_text_key(text)
        if upper in month_names:
            return month_names[upper]
        if text.isdigit():
            return text.zfill(2)
        return text

    return series.map(_normalize).astype("string")


def translate_sexo(series: pd.Series) -> pd.Series:
    def _translate(value: object) -> str:
        text = normalize_text(value)
        if not text:
            return "Sin información"
        text = text[:-2] if text.endswith(".0") else text
        return SEXO_LABELS.get(text.strip(), "Sin información")

    return series.map(_translate).astype("string")


def age_group_lookup() -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for item in AGE_GROUP_DEFINITIONS:
        for code in item["codes"]:
            lookup[str(code)] = {
                "categoria": item["label"],
                "rango": item["range"],
            }
    return lookup


def translate_age_group(series: pd.Series) -> pd.DataFrame:
    lookup = age_group_lookup()

    categories = []
    ranges = []
    order = []
    for value in series:
        text = normalize_text(value)
        if not text:
            categories.append("Sin información")
            ranges.append("Sin información")
            order.append(len(AGE_GROUP_ORDER) - 1)
            continue
        if text.endswith(".0"):
            text = text[:-2]
        info = lookup.get(text.strip())
        if info is None:
            categories.append("Sin información")
            ranges.append("Sin información")
            order.append(len(AGE_GROUP_ORDER) - 1)
            continue
        categories.append(info["categoria"])
        ranges.append(info["rango"])
        order.append(AGE_GROUP_ORDER.index(info["categoria"]))

    return pd.DataFrame(
        {
            "CATEGORIA_EDAD": pd.Series(categories, dtype="string"),
            "RANGO_EDAD": pd.Series(ranges, dtype="string"),
            "ORDEN_EDAD": pd.Series(order, dtype="int64"),
        }
    )


def prepare_deaths_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["COD_DANE"] = normalize_numeric_code(prepared["COD_DANE"], 5)
    prepared["COD_DEPARTAMENTO"] = normalize_numeric_code(prepared["COD_DEPARTAMENTO"], 2)
    prepared["COD_MUNICIPIO"] = normalize_numeric_code(prepared["COD_MUNICIPIO"], 3)
    prepared["COD_MUERTE"] = normalize_alphanumeric_code(prepared["COD_MUERTE"])
    prepared["MES"] = normalize_month_code(prepared["MES"])
    prepared["SEXO"] = prepared["SEXO"].map(normalize_text).astype("string")
    prepared["SEXO_LABEL"] = translate_sexo(prepared["SEXO"])

    age_info = translate_age_group(prepared["GRUPO_EDAD1"])
    prepared = pd.concat([prepared.reset_index(drop=True), age_info], axis=1)
    prepared["GRUPO_EDAD1"] = prepared["GRUPO_EDAD1"].map(normalize_text).astype("string")
    return prepared


def _clean_lookup_frame(df: pd.DataFrame, code_column: str, name_column: str, width: int) -> pd.DataFrame:
    clean = df[[code_column, name_column]].copy()
    clean[code_column] = normalize_numeric_code(clean[code_column], width)
    clean[name_column] = clean[name_column].map(normalize_text).replace("", pd.NA)
    clean = clean.dropna(subset=[code_column, name_column])
    clean = clean.drop_duplicates(subset=[code_column])
    return clean


def build_divipola_lookups(divipola_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    normalized_columns = {normalize_text_key(col): col for col in divipola_df.columns}

    dept_code_col = normalized_columns.get("COD_DEPARTAMENTO")
    dept_name_col = normalized_columns.get("DEPARTAMENTO")
    muni_code_col = normalized_columns.get("COD_DANE")
    muni_name_col = normalized_columns.get("MUNICIPIO")

    if not all([dept_code_col, dept_name_col, muni_code_col, muni_name_col]):
        raise ValueError("DIVIPOLA no contiene las columnas mínimas esperadas.")

    dept_lookup = _clean_lookup_frame(divipola_df, dept_code_col, dept_name_col, 2)
    muni_lookup = _clean_lookup_frame(divipola_df, muni_code_col, muni_name_col, 5)

    return dept_lookup, muni_lookup


def build_cause_lookup(cause_df: pd.DataFrame) -> pd.DataFrame:
    normalized_columns = [(normalize_text_key(col), col) for col in cause_df.columns]

    def _pick(*must_have: str) -> str | None:
        for normalized, original in normalized_columns:
            if all(token in normalized for token in must_have):
                return original
        return None

    code4_col = _pick("CODIGO", "CUATRO")
    desc4_col = _pick("DESCRIPCION", "CUATRO")
    code3_col = _pick("CODIGO", "TRES")
    desc3_col = _pick("DESCRIPCION", "TRES")

    if code4_col is None or desc4_col is None:
        raise ValueError("El diccionario de causas no expone columnas de código/descripción de 4 caracteres.")

    records = []
    for _, row in cause_df.iterrows():
        code4 = normalize_alphanumeric_code(pd.Series([row[code4_col]])).iloc[0]
        desc4 = normalize_text(row[desc4_col])
        code3 = normalize_alphanumeric_code(pd.Series([row[code3_col]])).iloc[0] if code3_col else ""
        desc3 = normalize_text(row[desc3_col]) if desc3_col else ""
        if code4 and desc4:
            records.append(
                {
                    "COD_MUERTE_4": code4,
                    "DESCRIPCION_4": desc4,
                    "COD_MUERTE_3": code3,
                    "DESCRIPCION_3": desc3,
                }
            )

    lookup = pd.DataFrame(records).drop_duplicates(subset=["COD_MUERTE_4"])
    return lookup


def resolve_cause_description(code: object, cause_lookup: pd.DataFrame) -> str:
    text = normalize_alphanumeric_code(pd.Series([code])).iloc[0]
    if not text:
        return "Sin información"

    exact = cause_lookup.loc[cause_lookup["COD_MUERTE_4"] == text, "DESCRIPCION_4"]
    if not exact.empty:
        return exact.iloc[0]

    prefix = text[:3]
    if prefix:
        prefix_exact = cause_lookup.loc[cause_lookup["COD_MUERTE_3"] == prefix, "DESCRIPCION_3"]
        if not prefix_exact.empty:
            return prefix_exact.iloc[0]

    return "Sin descripción"


def _count_by_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return (
        df.loc[df[column].notna() & (df[column] != "")]
        .groupby(column, dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )


def build_monthly_deaths(deaths_df: pd.DataFrame) -> pd.DataFrame:
    counts = _count_by_column(deaths_df, "MES")
    counts["MES"] = counts["MES"].astype(str).str.zfill(2)
    counts = counts.set_index("MES").reindex(MONTH_ORDER, fill_value=0).reset_index()
    counts["MES_NOMBRE"] = counts["MES"].map(MONTH_LABELS_ES)
    return counts[["MES", "MES_NOMBRE", "TOTAL"]]


def build_department_deaths(deaths_df: pd.DataFrame, dept_lookup: pd.DataFrame) -> pd.DataFrame:
    counts = _count_by_column(deaths_df, "COD_DEPARTAMENTO")
    result = counts.merge(dept_lookup, left_on="COD_DEPARTAMENTO", right_on="COD_DEPARTAMENTO", how="left")
    result = result.rename(columns={"DEPARTAMENTO": "NOMBRE_DEPARTAMENTO"})
    result["NOMBRE_DEPARTAMENTO"] = result["NOMBRE_DEPARTAMENTO"].fillna("Sin información")
    result = result[["COD_DEPARTAMENTO", "NOMBRE_DEPARTAMENTO", "TOTAL"]]
    result = result.sort_values(["TOTAL", "COD_DEPARTAMENTO"], ascending=[False, True]).reset_index(drop=True)
    return result


def build_violent_cities_x95(deaths_df: pd.DataFrame, muni_lookup: pd.DataFrame, dept_lookup: pd.DataFrame) -> pd.DataFrame:
    filtered = deaths_df.loc[deaths_df["COD_MUERTE"].str.startswith("X95", na=False)].copy()
    counts = _count_by_column(filtered, "COD_DANE")
    result = counts.merge(muni_lookup, on="COD_DANE", how="left")
    result = result.merge(
        deaths_df[["COD_DANE", "COD_DEPARTAMENTO"]].drop_duplicates(),
        on="COD_DANE",
        how="left",
    )
    result = result.merge(dept_lookup, on="COD_DEPARTAMENTO", how="left", suffixes=("", "_DEP"))
    result = result.rename(columns={"MUNICIPIO": "NOMBRE_MUNICIPIO", "DEPARTAMENTO": "NOMBRE_DEPARTAMENTO"})
    result = result.dropna(subset=["NOMBRE_MUNICIPIO"])
    result["NOMBRE_DEPARTAMENTO"] = result["NOMBRE_DEPARTAMENTO"].fillna("Sin información")
    result = result[["COD_DANE", "NOMBRE_MUNICIPIO", "NOMBRE_DEPARTAMENTO", "TOTAL"]]
    result = result.sort_values(["TOTAL", "NOMBRE_MUNICIPIO"], ascending=[False, True]).head(5).reset_index(drop=True)
    return result


def build_lowest_mortality_cities(deaths_df: pd.DataFrame, muni_lookup: pd.DataFrame, dept_lookup: pd.DataFrame) -> pd.DataFrame:
    counts = _count_by_column(deaths_df, "COD_DANE")
    result = counts.merge(muni_lookup, on="COD_DANE", how="left")
    result = result.merge(
        deaths_df[["COD_DANE", "COD_DEPARTAMENTO"]].drop_duplicates(),
        on="COD_DANE",
        how="left",
    )
    result = result.merge(dept_lookup, on="COD_DEPARTAMENTO", how="left", suffixes=("", "_DEP"))
    result = result.rename(columns={"MUNICIPIO": "NOMBRE_MUNICIPIO", "DEPARTAMENTO": "NOMBRE_DEPARTAMENTO"})
    result = result.dropna(subset=["NOMBRE_MUNICIPIO"])
    result["NOMBRE_DEPARTAMENTO"] = result["NOMBRE_DEPARTAMENTO"].fillna("Sin información")
    result = result[["COD_DANE", "NOMBRE_MUNICIPIO", "NOMBRE_DEPARTAMENTO", "TOTAL"]]
    result = result.sort_values(["TOTAL", "NOMBRE_MUNICIPIO"], ascending=[True, True]).head(10).reset_index(drop=True)
    return result


def build_top_causes(deaths_df: pd.DataFrame, cause_lookup: pd.DataFrame) -> pd.DataFrame:
    counts = _count_by_column(deaths_df, "COD_MUERTE")
    counts["CAUSA_DE_MUERTE"] = counts["COD_MUERTE"].map(lambda code: resolve_cause_description(code, cause_lookup))
    result = counts[["COD_MUERTE", "CAUSA_DE_MUERTE", "TOTAL"]]
    result = result.sort_values(["TOTAL", "COD_MUERTE"], ascending=[False, True]).head(10).reset_index(drop=True)
    return result


def build_sex_department(deaths_df: pd.DataFrame, dept_lookup: pd.DataFrame) -> pd.DataFrame:
    counts = (
        deaths_df.loc[deaths_df["COD_DEPARTAMENTO"].notna() & (deaths_df["COD_DEPARTAMENTO"] != "")]
        .groupby(["COD_DEPARTAMENTO", "SEXO_LABEL"], dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )
    result = counts.merge(dept_lookup, on="COD_DEPARTAMENTO", how="left")
    result = result.rename(columns={"DEPARTAMENTO": "NOMBRE_DEPARTAMENTO"})
    result["NOMBRE_DEPARTAMENTO"] = result["NOMBRE_DEPARTAMENTO"].fillna("Sin información")
    result = result[["COD_DEPARTAMENTO", "NOMBRE_DEPARTAMENTO", "SEXO_LABEL", "TOTAL"]]
    result = result.sort_values(["COD_DEPARTAMENTO", "SEXO_LABEL"]).reset_index(drop=True)
    return result


def build_age_group(deaths_df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        deaths_df.groupby(["CATEGORIA_EDAD", "RANGO_EDAD", "ORDEN_EDAD"], dropna=False)
        .size()
        .reset_index(name="TOTAL")
    )
    counts = counts.sort_values("ORDEN_EDAD").reset_index(drop=True)
    counts["CATEGORIA_EDAD"] = pd.Categorical(counts["CATEGORIA_EDAD"], categories=AGE_GROUP_ORDER, ordered=True)
    counts = counts.sort_values("CATEGORIA_EDAD").reset_index(drop=True)
    return counts[["CATEGORIA_EDAD", "RANGO_EDAD", "TOTAL", "ORDEN_EDAD"]]


def build_kpis(
    deaths_df: pd.DataFrame,
    department_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    causes_df: pd.DataFrame,
    violent_cities_df: pd.DataFrame,
) -> dict:
    total_deaths = int(len(deaths_df))
    top_department = department_df.iloc[0] if not department_df.empty else None
    top_month = monthly_df.sort_values("TOTAL", ascending=False).iloc[0] if not monthly_df.empty else None
    top_cause = causes_df.iloc[0] if not causes_df.empty else None
    top_city = violent_cities_df.iloc[0] if not violent_cities_df.empty else None

    return {
        "total_deaths": total_deaths,
        "top_department": {
            "name": None if top_department is None else top_department["NOMBRE_DEPARTAMENTO"],
            "code": None if top_department is None else top_department["COD_DEPARTAMENTO"],
            "total": None if top_department is None else int(top_department["TOTAL"]),
        },
        "top_month": {
            "name": None if top_month is None else top_month["MES_NOMBRE"],
            "code": None if top_month is None else top_month["MES"],
            "total": None if top_month is None else int(top_month["TOTAL"]),
        },
        "top_cause": {
            "code": None if top_cause is None else top_cause["COD_MUERTE"],
            "name": None if top_cause is None else top_cause["CAUSA_DE_MUERTE"],
            "total": None if top_cause is None else int(top_cause["TOTAL"]),
        },
        "top_x95_city": {
            "name": None if top_city is None else top_city["NOMBRE_MUNICIPIO"],
            "department": None if top_city is None else top_city["NOMBRE_DEPARTAMENTO"],
            "code": None if top_city is None else top_city["COD_DANE"],
            "total": None if top_city is None else int(top_city["TOTAL"]),
        },
    }


def to_jsonable(obj: object) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)
