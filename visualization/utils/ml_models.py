import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import streamlit as st


@st.cache_resource
def train_range_prediction_model(df):
    """Train range prediction model"""
    expanded_rows = []
    for _, row in df.iterrows():
        expanded_rows.extend([row.to_dict()] * int(row["vehicle_count"]))
    df_expanded = pd.DataFrame(expanded_rows)
    df_expanded = df_expanded.drop("vehicle_count", axis=1)

    le_make = LabelEncoder()
    le_model = LabelEncoder()
    le_ev_type = LabelEncoder()
    le_cafv = LabelEncoder()
    le_state = LabelEncoder()

    df_expanded["make_encoded"] = le_make.fit_transform(df_expanded["make"])
    df_expanded["model_encoded"] = le_model.fit_transform(df_expanded["model"])
    df_expanded["ev_type_encoded"] = le_ev_type.fit_transform(df_expanded["ev_type"])
    df_expanded["cafv_encoded"] = le_cafv.fit_transform(df_expanded["cafv_eligibility"])
    df_expanded["state_encoded"] = le_state.fit_transform(df_expanded["state"])

    features = [
        "model_year",
        "make_encoded",
        "model_encoded",
        "ev_type_encoded",
        "cafv_encoded",
        "state_encoded",
    ]
    X = df_expanded[features]
    y = df_expanded["electric_range"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    feature_importance = pd.DataFrame(
        {
            "feature": ["Model Year", "Make", "Model", "EV Type", "CAFV", "State"],
            "importance": model.feature_importances_,
        }
    ).sort_values("importance", ascending=False)

    return {
        "model": model,
        "encoders": {
            "make": le_make,
            "model": le_model,
            "ev_type": le_ev_type,
            "cafv": le_cafv,
            "state": le_state,
        },
        "metrics": {"mae": mae, "rmse": rmse, "r2": r2},
        "predictions": {"y_test": y_test, "y_pred": y_pred},
        "feature_importance": feature_importance,
    }


def forecast_adoption(df, years_ahead=5, degree=2):
    """Forecast future adoption using polynomial regression"""
    yearly_data = df.groupby("model_year")["vehicle_count"].sum().reset_index()
    yearly_data = yearly_data.sort_values("model_year")

    X = yearly_data["model_year"].values.reshape(-1, 1)
    y = yearly_data["vehicle_count"].values

    poly_features = PolynomialFeatures(degree=degree)
    X_poly = poly_features.fit_transform(X)

    model = LinearRegression()
    model.fit(X_poly, y)

    y_pred = model.predict(X_poly)
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    last_year = int(yearly_data["model_year"].max())
    future_years = np.array(range(last_year + 1, last_year + years_ahead + 1)).reshape(
        -1, 1
    )
    future_X_poly = poly_features.transform(future_years)
    future_predictions = model.predict(future_X_poly)

    results = pd.DataFrame(
        {"year": future_years.flatten(), "predicted_vehicles": future_predictions}
    )

    return {
        "historical": yearly_data,
        "predictions": results,
        "model_fit": {"mae": mae, "r2": r2, "fitted_values": y_pred},
        "fitted_values": y_pred,
    }
