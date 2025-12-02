import pandas as pd

from web.utils.analytics import create_scatter_with_trendline


def test_scatter_trendline_works_without_scipy_or_statsmodels():
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    df = pd.DataFrame(
        {
            "date": list(dates) * 2,
            "metric_name": ["x"] * 3 + ["y"] * 3,
            "value": [1.0, 2.0, 3.0, 2.0, 4.0, 6.0],
        }
    )

    html, correlation, p_value = create_scatter_with_trendline(df, "x", "y")

    assert "Trendline" in html
    assert correlation == 1.0
    assert p_value is None
