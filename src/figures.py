from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go

from src.config import MONTH_LABELS_ES, MONTH_ORDER, SEXO_LABELS


COLOR_SCALE = [
    [0.0, "#E6F2F8"],
    [0.25, "#A7D0E4"],
    [0.5, "#5BA3C8"],
    [0.75, "#2F6D8A"],
    [1.0, "#184E63"],
]

SEQUENCE_COLORS = ["#1F4E79", "#4C78A8", "#F58518", "#54A24B", "#E45756", "#72B7B2", "#B279A2"]


def _base_layout(fig: go.Figure, title: str) -> go.Figure:
    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        template="plotly_white",
        margin=dict(l=20, r=20, t=70, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        font=dict(family="Arial, sans-serif", size=13, color="#1F2937"),
    )
    return fig


def make_department_map(df: pd.DataFrame, geojson_colombia: dict[str, Any]) -> go.Figure:
    fig = go.Figure(
        go.Choropleth(
            geojson=geojson_colombia,
            locations=df["COD_DEPARTAMENTO"],
            z=df["TOTAL"],
            featureidkey="properties.DPTO",
            colorscale=COLOR_SCALE,
            marker_line_color="white",
            marker_line_width=0.7,
            colorbar_title="Defunciones",
            customdata=df[["NOMBRE_DEPARTAMENTO", "COD_DEPARTAMENTO"]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Código: %{customdata[1]}<br>"
                "Total de muertes: %{z}<extra></extra>"
            ),
        )
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(coloraxis_showscale=False)
    return _base_layout(fig, "Distribución total de muertes por departamento, Colombia 2019")


def make_monthly_line(df: pd.DataFrame) -> go.Figure:
    ordered = df.copy()
    order_map = {month: index for index, month in enumerate(MONTH_ORDER)}
    ordered["_ORDER"] = ordered["MES"].map(order_map)
    ordered = ordered.sort_values("_ORDER")

    fig = go.Figure(
        go.Scatter(
            x=ordered["MES_NOMBRE"],
            y=ordered["TOTAL"],
            mode="lines+markers",
            line=dict(color="#1F4E79", width=3),
            marker=dict(size=9, color="#F58518"),
            hovertemplate="<b>%{x}</b><br>Total de muertes: %{y}<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Mes")
    fig.update_yaxes(title_text="Total de muertes", rangemode="tozero")
    return _base_layout(fig, "Total de muertes por mes en Colombia, 2019")


def make_violent_cities_bar(df: pd.DataFrame) -> go.Figure:
    ordered = df.sort_values("TOTAL", ascending=True)
    labels = ordered["NOMBRE_MUNICIPIO"] + " - " + ordered["NOMBRE_DEPARTAMENTO"]
    fig = go.Figure(
        go.Bar(
            x=ordered["TOTAL"],
            y=labels,
            orientation="h",
            marker_color="#C0392B",
            text=ordered["TOTAL"],
            textposition="outside",
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Código DANE: %{customdata[0]}<br>"
                "Total de casos: %{x}<extra></extra>"
            ),
            customdata=ordered[["COD_DANE"]],
        )
    )
    fig.update_xaxes(title_text="Total de casos")
    fig.update_yaxes(title_text="Ciudad", automargin=True)
    return _base_layout(fig, "Cinco ciudades con mayor número de homicidios por armas de fuego, código X95")


def make_lowest_mortality_pie(df: pd.DataFrame) -> go.Figure:
    labels = df["NOMBRE_MUNICIPIO"] + " - " + df["NOMBRE_DEPARTAMENTO"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=df["TOTAL"],
            hole=0.35,
            textinfo="label+percent",
            marker=dict(colors=SEQUENCE_COLORS),
            hovertemplate="<b>%{label}</b><br>Total de defunciones: %{value}<extra></extra>",
        )
    )
    return _base_layout(fig, "Diez ciudades con menor mortalidad registrada, 2019")


def make_top_causes_table_data(df: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    table = df.rename(
        columns={
            "COD_MUERTE": "Código",
            "CAUSA_DE_MUERTE": "Causa de muerte",
            "TOTAL": "Total de casos",
        }
    ).copy()
    table["Total de casos"] = table["Total de casos"].astype(int)
    records = table[["Código", "Causa de muerte", "Total de casos"]].to_dict("records")
    columns = [
        {"name": "Código", "id": "Código"},
        {"name": "Causa de muerte", "id": "Causa de muerte"},
        {"name": "Total de casos", "id": "Total de casos"},
    ]
    return records, columns


def make_sex_department_stacked_bar(df: pd.DataFrame) -> go.Figure:
    departments = sorted(df["NOMBRE_DEPARTAMENTO"].dropna().unique().tolist())
    fig = go.Figure()
    for sexo in ["Hombre", "Mujer", "Indeterminado", "Sin información"]:
        subset = df.loc[df["SEXO_LABEL"] == sexo].copy()
        subset = (
            pd.DataFrame({"NOMBRE_DEPARTAMENTO": departments})
            .merge(subset[["NOMBRE_DEPARTAMENTO", "TOTAL"]], on="NOMBRE_DEPARTAMENTO", how="left")
            .fillna({"TOTAL": 0})
        )
        subset["TOTAL"] = subset["TOTAL"].astype(int)
        fig.add_trace(
            go.Bar(
                x=subset["NOMBRE_DEPARTAMENTO"],
                y=subset["TOTAL"],
                name=sexo,
                text=subset["TOTAL"],
                textposition="auto",
                hovertemplate=(
                    "<b>%{x}</b><br>"
                    f"Sexo: {sexo}<br>"
                    "Total de muertes: %{y}<extra></extra>"
                ),
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Departamento", tickangle=-45)
    fig.update_yaxes(title_text="Total de muertes", rangemode="tozero")
    return _base_layout(fig, "Muertes por sexo en cada departamento, 2019")


def make_age_group_bar(df: pd.DataFrame) -> go.Figure:
    ordered = df.sort_values("ORDEN_EDAD")
    fig = go.Figure(
        go.Bar(
            x=ordered["CATEGORIA_EDAD"],
            y=ordered["TOTAL"],
            marker_color="#4C78A8",
            text=ordered["TOTAL"],
            textposition="auto",
            customdata=ordered[["RANGO_EDAD"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Rango de edad: %{customdata[0]}<br>"
                "Total de muertes: %{y}<extra></extra>"
            ),
        )
    )
    fig.update_xaxes(title_text="Categoría de edad", tickangle=-35)
    fig.update_yaxes(title_text="Total de muertes", rangemode="tozero")
    return _base_layout(fig, "Distribución de muertes por grupo de edad, 2019")
