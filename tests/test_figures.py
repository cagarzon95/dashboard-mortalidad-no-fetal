from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from src.config import PROCESSED_FILES
from src.data_loader import load_dashboard_bundle
from src.figures import (
    make_age_group_bar,
    make_department_map,
    make_lowest_mortality_pie,
    make_monthly_line,
    make_sex_department_stacked_bar,
    make_violent_cities_bar,
)
from src.layout import build_layout


def _bundle():
    bundle = load_dashboard_bundle()
    assert bundle.ready, bundle.message
    return bundle


def test_each_figure_is_valid_plotly():
    bundle = _bundle()
    figs = [
        make_department_map(bundle.deaths_by_department, bundle.geojson),
        make_monthly_line(bundle.deaths_by_month),
        make_violent_cities_bar(bundle.top_violent_cities_x95),
        make_lowest_mortality_pie(bundle.lowest_mortality_cities),
        make_sex_department_stacked_bar(bundle.deaths_by_sex_department),
        make_age_group_bar(bundle.deaths_by_age_group),
    ]
    for fig in figs:
        assert isinstance(fig, go.Figure)
        assert fig.to_plotly_json()


def test_app_layout_builds():
    bundle = _bundle()
    layout = build_layout(bundle)
    assert layout is not None

