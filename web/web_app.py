import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from flask import Flask, render_template

app = Flask(__name__, static_folder="static")
DB_PATH = "../BNASFR02.DB"

def read_df(table):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table}", con)
    con.close()
    return df

@app.route("/")
def dashboard():
    # Read property data
    rentals = read_df("BNA_RENTALS")
    forsale = read_df("BNA_FORSALE")

    # Read FRED metrics data
    try:
        fred_metrics = read_df("BNA_FRED_METRICS")
        fred_metrics['date'] = pd.to_datetime(fred_metrics['date'])
    except:
        fred_metrics = pd.DataFrame()

    # Property KPIs
    property_kpis = {
        "Total Rental Listings": len(rentals),
        "Avg Rental Price": f"${round(float(rentals['price'].mean())):,}" if "price" in rentals.columns and len(rentals) > 0 else "N/A",
        "Total For-Sale Listings": len(forsale),
        "Avg Sale Price": f"${round(float(forsale['price'].mean())):,}" if "price" in forsale.columns and len(forsale) > 0 else "N/A",
    }

    # FRED Economic KPIs (latest values)
    fred_kpis = {}
    if not fred_metrics.empty:
        latest_metrics = fred_metrics.sort_values('date').groupby('metric_name').last()

        metric_display_names = {
            'median_price': 'Median Listing Price',
            'active_listings': 'Active Listings',
            'median_dom': 'Median Days on Market',
            'employment_non_farm': 'Non-Farm Employment',
            'msa_population': 'MSA Population',
            'msa_per_capita_income': 'Per Capita Income'
        }

        for metric_name, display_name in metric_display_names.items():
            if metric_name in latest_metrics.index:
                value = latest_metrics.loc[metric_name, 'value']
                if metric_name == 'median_price':
                    fred_kpis[display_name] = f"${int(value):,}"
                elif metric_name in ['active_listings', 'median_dom']:
                    fred_kpis[display_name] = f"{int(value):,}"
                elif metric_name == 'employment_non_farm':
                    fred_kpis[display_name] = f"{int(value/1000)}K"
                elif metric_name == 'msa_population':
                    fred_kpis[display_name] = f"{int(value/1000)}K"
                elif metric_name == 'msa_per_capita_income':
                    fred_kpis[display_name] = f"${int(value):,}"

    # Rental price histogram
    fig_rent_hist = px.histogram(
        rentals,
        x="price",
        title="Rental Price Distribution",
        labels={'price': 'Monthly Rent ($)', 'count': 'Number of Listings'},
        color_discrete_sequence=['#1f77b4']
    )
    fig_rent_hist.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=12),
        title_font_size=16,
        showlegend=False
    )

    # For-sale price histogram
    fig_sale_hist = px.histogram(
        forsale,
        x="price",
        title="For-Sale Price Distribution",
        labels={'price': 'Sale Price ($)', 'count': 'Number of Listings'},
        color_discrete_sequence=['#2ca02c']
    )
    fig_sale_hist.update_layout(
        template="plotly_white",
        font=dict(family="Arial, sans-serif", size=12),
        title_font_size=16,
        showlegend=False
    )

    # FRED metrics time series charts
    fred_charts = {}
    if not fred_metrics.empty:
        # Median price trend
        median_price_data = fred_metrics[fred_metrics['metric_name'] == 'median_price'].sort_values('date')
        if not median_price_data.empty:
            fig_median_price = px.line(
                median_price_data,
                x='date',
                y='value',
                title='Median Listing Price Over Time',
                labels={'date': 'Date', 'value': 'Price ($)'}
            )
            fig_median_price.update_traces(line_color='#ff7f0e', line_width=2)
            fig_median_price.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                hovermode='x unified'
            )
            fred_charts['median_price'] = pio.to_html(fig_median_price, full_html=False, include_plotlyjs=False)

        # Active listings trend
        active_listings_data = fred_metrics[fred_metrics['metric_name'] == 'active_listings'].sort_values('date')
        if not active_listings_data.empty:
            fig_active = px.line(
                active_listings_data,
                x='date',
                y='value',
                title='Active Listings Over Time',
                labels={'date': 'Date', 'value': 'Number of Listings'}
            )
            fig_active.update_traces(line_color='#d62728', line_width=2)
            fig_active.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                hovermode='x unified'
            )
            fred_charts['active_listings'] = pio.to_html(fig_active, full_html=False, include_plotlyjs=False)

        # Employment trend
        employment_data = fred_metrics[fred_metrics['metric_name'] == 'employment_non_farm'].sort_values('date')
        if not employment_data.empty:
            fig_employment = px.line(
                employment_data,
                x='date',
                y='value',
                title='Non-Farm Employment Over Time',
                labels={'date': 'Date', 'value': 'Employment (thousands)'}
            )
            fig_employment.update_traces(line_color='#9467bd', line_width=2)
            fig_employment.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                hovermode='x unified'
            )
            fred_charts['employment'] = pio.to_html(fig_employment, full_html=False, include_plotlyjs=False)

        # Days on market trend
        dom_data = fred_metrics[fred_metrics['metric_name'] == 'median_dom'].sort_values('date')
        if not dom_data.empty:
            fig_dom = px.line(
                dom_data,
                x='date',
                y='value',
                title='Median Days on Market Over Time',
                labels={'date': 'Date', 'value': 'Days'}
            )
            fig_dom.update_traces(line_color='#8c564b', line_width=2)
            fig_dom.update_layout(
                template="plotly_white",
                font=dict(family="Arial, sans-serif", size=12),
                title_font_size=16,
                hovermode='x unified'
            )
            fred_charts['dom'] = pio.to_html(fig_dom, full_html=False, include_plotlyjs=False)

    plots = {
        "rent_price_hist": pio.to_html(fig_rent_hist, full_html=False, include_plotlyjs="cdn"),
        "sale_price_hist": pio.to_html(fig_sale_hist, full_html=False, include_plotlyjs=False),
    }

    return render_template(
        "dashboard.html",
        property_kpis=property_kpis,
        fred_kpis=fred_kpis,
        plots=plots,
        fred_charts=fred_charts,
        rentals=rentals,
        forsale=forsale
    )

if __name__ == "__main__":
    app.run(debug=True)
