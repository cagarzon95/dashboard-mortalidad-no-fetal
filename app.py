from __future__ import annotations

from dash import Dash

from src.data_loader import load_dashboard_bundle
from src.layout import build_error_layout, build_layout


bundle = load_dashboard_bundle()

app = Dash(__name__, title="Mortalidad no fetal en Colombia, 2019", suppress_callback_exceptions=True)
app.layout = build_layout(bundle) if bundle.ready else build_error_layout(bundle.message)

server = app.server


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)

