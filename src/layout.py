from __future__ import annotations

from typing import Any

from dash import dcc, dash_table, html

from src.figures import (
    make_age_group_bar,
    make_department_map,
    make_lowest_mortality_pie,
    make_monthly_line,
    make_sex_department_stacked_bar,
    make_top_causes_table_data,
    make_violent_cities_bar,
)


def _kpi_card(title: str, value: str, subtitle: str | None = None) -> html.Div:
    children = [
        html.Div(title, className="kpi-title"),
        html.Div(value, className="kpi-value"),
    ]
    if subtitle:
        children.append(html.Div(subtitle, className="kpi-subtitle"))
    return html.Div(children, className="kpi-card")


def _section(title: str, description: str, figure_component: Any) -> html.Section:
    return html.Section(
        className="panel",
        children=[
            html.H2(title, className="panel-title"),
            html.P(description, className="panel-description"),
            figure_component,
        ],
    )


def _fmt_number(value: int | None) -> str:
    if value is None:
        return "Sin datos"
    return f"{int(value):,}".replace(",", ".")


def _safe_text(value, default: str = "Sin datos") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text and text.lower() != "none" else default


def build_error_layout(message: str) -> html.Div:
    return html.Div(
        className="page",
        children=[
            html.Header(
                className="hero",
                children=[
                    html.H1("Mortalidad no fetal en Colombia, 2019"),
                    html.P("La aplicación no pudo cargar los archivos procesados."),
                ],
            ),
            html.Div(
                className="error-box",
                children=[
                    html.H2("Faltan archivos procesados"),
                    html.Pre(message, className="error-message"),
                ],
            ),
        ],
    )


def build_layout(bundle) -> html.Div:
    kpis = bundle.kpis or {}
    department_map = bundle.deaths_by_department
    monthly = bundle.deaths_by_month
    violent = bundle.top_violent_cities_x95
    lowest = bundle.lowest_mortality_cities
    top_causes = bundle.top_causes
    sex_dep = bundle.deaths_by_sex_department
    age_group = bundle.deaths_by_age_group

    table_records, table_columns = make_top_causes_table_data(top_causes)

    return html.Div(
        className="page",
        children=[
            html.Header(
                className="hero",
                children=[
                    html.H1("Mortalidad no fetal en Colombia, 2019"),
                    html.P(
                        "Explora patrones territoriales, temporales, demográficos y causales de la "
                        "mortalidad no fetal en Colombia durante 2019."
                    ),
                ],
            ),
            html.Section(
                className="kpi-grid",
                children=[
                    _kpi_card(
                        "Total de defunciones registradas",
                        _fmt_number(kpis.get("total_deaths")),
                    ),
                    _kpi_card(
                        "Departamento con mayor número de defunciones",
                        _safe_text(kpis.get("top_department", {}).get("name")),
                        _fmt_number(kpis.get("top_department", {}).get("total")),
                    ),
                    _kpi_card(
                        "Mes con mayor número de defunciones",
                        _safe_text(kpis.get("top_month", {}).get("name")),
                        _fmt_number(kpis.get("top_month", {}).get("total")),
                    ),
                    _kpi_card(
                        "Principal causa de muerte",
                        _safe_text(kpis.get("top_cause", {}).get("name")),
                        f"Código {_safe_text(kpis.get('top_cause', {}).get('code'), 'N/D')}",
                    ),
                    _kpi_card(
                        "Ciudad con más homicidios X95",
                        _safe_text(kpis.get("top_x95_city", {}).get("name")),
                        f"{kpis.get('top_x95_city', {}).get('department', 'Sin datos')} - "
                        f"{_fmt_number(kpis.get('top_x95_city', {}).get('total'))}",
                    ),
                ],
            ),
            _section(
                "Mapa coroplético",
                "La intensidad del color muestra la concentración total de defunciones por departamento.",
                dcc.Graph(
                    figure=make_department_map(department_map, bundle.geojson),
                    config={"displaylogo": False, "responsive": True},
                ),
            ),
            _section(
                "Serie mensual",
                "Permite identificar la estacionalidad de las defunciones durante 2019.",
                dcc.Graph(
                    figure=make_monthly_line(monthly),
                    config={"displaylogo": False, "responsive": True},
                ),
            ),
            _section(
                "Ciudades violentas",
                "Filtra registros con causas de muerte asociadas a códigos X95 para destacar las cinco ciudades con más casos.",
                dcc.Graph(
                    figure=make_violent_cities_bar(violent),
                    config={"displaylogo": False, "responsive": True},
                ),
            ),
            _section(
                "Mortalidad menor",
                "El gráfico muestra conteo absoluto de defunciones; no representa una tasa poblacional.",
                html.Div(
                    children=[
                        dcc.Graph(
                            figure=make_lowest_mortality_pie(lowest),
                            config={"displaylogo": False, "responsive": True},
                        ),
                        html.P(
                            "Nota metodológica: se presenta el menor número absoluto de defunciones registradas. "
                            "No corresponde a una tasa poblacional porque el conjunto de datos no incluye población municipal.",
                            className="method-note",
                        ),
                    ]
                ),
            ),
            html.Section(
                className="panel",
                children=[
                    html.H2("Diez principales causas de muerte en Colombia, 2019", className="panel-title"),
                    html.P(
                        "La tabla combina el código de muerte con la descripción textual del diccionario oficial.",
                        className="panel-description",
                    ),
                    dash_table.DataTable(
                        data=table_records,
                        columns=table_columns,
                        page_action="none",
                        sort_action="native",
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "fontFamily": "Arial, sans-serif",
                            "fontSize": "14px",
                            "padding": "12px",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "textAlign": "left",
                        },
                        style_header={
                            "backgroundColor": "#1F4E79",
                            "color": "white",
                            "fontWeight": "bold",
                        },
                        style_data={"backgroundColor": "white"},
                        style_data_conditional=[
                            {"if": {"row_index": "odd"}, "backgroundColor": "#F7FAFC"},
                        ],
                    ),
                ],
            ),
            _section(
                "Sexo por departamento",
                "La composición por sexo muestra cómo se distribuyen las muertes en cada territorio.",
                dcc.Graph(
                    figure=make_sex_department_stacked_bar(sex_dep),
                    config={"displaylogo": False, "responsive": True},
                ),
            ),
            _section(
                "Grupo de edad",
                "Los grupos de edad siguen la clasificación solicitada para el análisis del ciclo de vida.",
                dcc.Graph(
                    figure=make_age_group_bar(age_group),
                    config={"displaylogo": False, "responsive": True},
                ),
            ),
            html.Footer(
                className="footer",
                children=[
                    html.P(
                        "Fuente: registros oficiales de mortalidad no fetal 2019, diccionario de causas, DIVIPOLA y geojson departamental."
                    )
                ],
            ),
        ],
    )
