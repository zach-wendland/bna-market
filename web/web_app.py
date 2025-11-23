import sqlite3
import pandas as pd
import plotly.express as px
import plotly.io as pio
from flask import Flask, render_template

app = Flask(__name__, static_folder="static")
DB_PATH = "BNASFR02.db"

def read_df(table):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table}", con)
    con.close()
    return df

@app.route("/")
def dashboard():
    rentals = read_df("BNA_RENTALS")
    forsale = read_df("BNA_FORSALE")

    kpis = {
        "Total Rental Listings": len(rentals),
        "Avg Rental Price": float(rentals["price"].mean()) if "price" in rentals else None,
        "New Rentals This Week": int(
            (pd.to_datetime(rentals["scraped_at"]).dt.date
             >= pd.Timestamp.today().date() - pd.Timedelta(days=7)).sum()
        ) if "scraped_at" in rentals else None
    }

    fig_price_hist = px.histogram(
        rentals, x="price", nbins=30, title="Rental Price Distribution"
    )

    fig_time_trend = (
        px.line(
            rentals.groupby(
                pd.to_datetime(rentals["scraped_at"]).dt.date, as_index=False
            )["price"].mean(),
            x="scraped_at",
            y="price",
            title="Average Rental Price Over Time"
        )
        if "scraped_at" in rentals and "price" in rentals
        else px.line(title="Average Rental Price Over Time")
    )

    plots = {
        "rent_price_hist": pio.to_html(fig_price_hist, full_html=False, include_plotlyjs="cdn"),
        "rent_time_trend": pio.to_html(fig_time_trend, full_html=False, include_plotlyjs=False),
    }

    return render_template(
        "dashboard.html",
        kpis=kpis,
        plots=plots,
        rentals=rentals,
        forsale=forsale
    )

if __name__ == "__main__":
    app.run(debug=True)
