from fredapi import Fred
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()


def fredMetricsPipe01() -> pd.DataFrame:
    """
    Fetch FRED economic indicators for Nashville MSA.
    Returns a long-format DataFrame with 15 years of historical data.
    """
    fred = Fred(api_key=os.getenv("FRED_API_KEY"))

    # Define FRED series IDs for Nashville MSA economic indicators
    series_ids = {
        'active_listings': 'ACTLISCOU34980',
        'median_price': 'MEDLISPRI34980',
        'median_dom': 'MEDDAYONMAR34980',
        'employment_non_farm': 'NASH947NA',
        'msa_population': 'NVLPOP',
        'median_pp_sqft': 'MEDLISPRIPERSQUFEE34980',
        'median_listing_price_change': 'MEDLISPRIMM47037',
        'msa_per_capita_income': 'NASH947PCPI'
    }

    # Calculate date range: 15 years back from today (11/28/2025)
    end_date = datetime(2025, 11, 28)
    start_date = end_date - timedelta(days=15*365)

    # Fetch all series and combine into single DataFrame
    all_data = []

    for metric_name, series_id in series_ids.items():
        try:
            # Fetch series data with observation start/end dates
            series = fred.get_series(
                series_id,
                observation_start=start_date.strftime('%Y-%m-%d'),
                observation_end=end_date.strftime('%Y-%m-%d')
            )

            # Convert to DataFrame
            df = series.to_frame(name='value')
            df['metric_name'] = metric_name
            df['series_id'] = series_id
            df.reset_index(inplace=True)
            df.rename(columns={'index': 'date'}, inplace=True)

            all_data.append(df)
            print(f"Fetched {len(df)} observations for {metric_name}")

        except Exception as e:
            print(f"Error fetching {metric_name} ({series_id}): {e}")
            continue

    if all_data:
        result_df = pd.concat(all_data, ignore_index=True)
        print(f"\nTotal observations collected: {len(result_df)}")
        return result_df
    else:
        print("No FRED data was collected.")
        return pd.DataFrame(columns=['date', 'metric_name', 'series_id', 'value'])
