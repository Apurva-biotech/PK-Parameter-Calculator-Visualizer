"""Streamlit web application for PK analysis."""

from __future__ import annotations

from dataclasses import asdict
from io import StringIO

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from calculator import (
    REQUIRED_COLUMNS,
    PKParameters,
    calculate_pk_parameters,
    validate_concentration_data,
)
from models.one_compartment import (
    OneCompartmentFit,
    concentration_time_model,
    fit_one_compartment_model,
)


st.set_page_config(
    page_title="PK Parameter Calculator",
    page_icon="PK",
    layout="wide",
)


def load_uploaded_data(uploaded_file: object | None) -> pd.DataFrame:
    """Load uploaded CSV data or fall back to the bundled sample dataset."""

    if uploaded_file is None:
        data = pd.read_csv("data/sample_data.csv")
    else:
        data = pd.read_csv(uploaded_file)

    validate_concentration_data(data)
    return data.loc[:, REQUIRED_COLUMNS].copy()


def create_results_table(parameters: PKParameters, model_fit: OneCompartmentFit) -> pd.DataFrame:
    """Convert PK and model-fit results into a download-friendly table."""

    rows = [
        ("Cmax", parameters.cmax),
        ("Tmax", parameters.tmax),
        ("AUC0-last", parameters.auc),
        ("ke", parameters.ke),
        ("Half-life", parameters.half_life),
        ("Vd", parameters.vd),
        ("Clearance", parameters.clearance),
        ("Fitted C0", model_fit.c0),
        ("Fitted ke", model_fit.ke),
    ]
    return pd.DataFrame(rows, columns=["parameter", "value"])


def create_interactive_plot(data: pd.DataFrame, model_fit: OneCompartmentFit) -> go.Figure:
    """Create an interactive concentration-time Plotly figure."""

    time = data["time"].to_numpy(dtype=float)
    concentration = data["concentration"].to_numpy(dtype=float)
    model_time = np.linspace(float(time.min()), float(time.max()), 300)
    model_concentration = concentration_time_model(model_time, model_fit.c0, model_fit.ke)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=time,
            y=concentration,
            mode="markers",
            name="Observed data",
            marker={"size": 9, "color": "#1f77b4"},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=model_time,
            y=model_concentration,
            mode="lines",
            name="One-compartment fit",
            line={"width": 3, "color": "#d62728"},
        )
    )
    figure.update_layout(
        title="Plasma Concentration-Time Profile",
        xaxis_title="Time",
        yaxis_title="Plasma concentration",
        hovermode="x unified",
        template="plotly_white",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        margin={"l": 40, "r": 20, "t": 80, "b": 40},
    )
    return figure


def results_to_csv(results: pd.DataFrame) -> bytes:
    """Serialize results table as CSV bytes for Streamlit downloads."""

    buffer = StringIO()
    results.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def render_metrics(parameters: PKParameters, model_fit: OneCompartmentFit) -> None:
    """Display calculated PK and fitted model parameters."""

    parameter_values = asdict(parameters)
    labels = {
        "cmax": "Cmax",
        "tmax": "Tmax",
        "auc": "AUC0-last",
        "ke": "ke",
        "half_life": "Half-life",
        "vd": "Vd",
        "clearance": "Clearance",
    }

    cols = st.columns(4)
    for index, (key, value) in enumerate(parameter_values.items()):
        cols[index % len(cols)].metric(labels[key], f"{value:.4f}")

    st.subheader("One-Compartment Model Fit")
    fit_cols = st.columns(2)
    fit_cols[0].metric("Fitted C0", f"{model_fit.c0:.4f}")
    fit_cols[1].metric("Fitted ke", f"{model_fit.ke:.4f}")


def main() -> None:
    """Run the Streamlit PK analysis app."""

    st.title("PK Parameter Calculator & Visualizer")
    st.caption(
        "Upload plasma concentration-time data, estimate PK parameters, "
        "and fit a one-compartment IV bolus model."
    )

    with st.sidebar:
        st.header("Analysis Inputs")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        dose = st.number_input("Dose", min_value=0.0001, value=1000.0, step=10.0)
        terminal_points = st.number_input(
            "Terminal points for ke",
            min_value=3,
            max_value=10,
            value=3,
            step=1,
        )

    try:
        data = load_uploaded_data(uploaded_file)
        model_fit = fit_one_compartment_model(
            data["time"].to_numpy(dtype=float),
            data["concentration"].to_numpy(dtype=float),
        )
        parameters = calculate_pk_parameters(
            data,
            dose=dose,
            c0=model_fit.c0,
            terminal_points=int(terminal_points),
        )
    except Exception as exc:
        st.error(f"Unable to analyze dataset: {exc}")
        st.stop()

    st.subheader("Input Data")
    st.dataframe(data, width="stretch", hide_index=True)

    st.subheader("Calculated Parameters")
    render_metrics(parameters, model_fit)

    st.subheader("Interactive Concentration-Time Plot")
    st.plotly_chart(create_interactive_plot(data, model_fit), width="stretch")

    results = create_results_table(parameters, model_fit)
    st.subheader("Download Results")
    st.dataframe(results, width="stretch", hide_index=True)
    st.download_button(
        label="Download results CSV",
        data=results_to_csv(results),
        file_name="pk_results.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
