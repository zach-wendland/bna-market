import sqlite3
import pandas as pd
import json
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01
from pipelines.otherMetricsPipe import fredMetricsPipe01

def updateSalesTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = forSalePipe01().copy()

    # Skip if no data was fetched
    if df.empty:
        print("Skipping BNA_FORSALE table update - no data available")
        conn.close()
        return

    # Read existing data
    try:
        existing_df = pd.read_sql_query("SELECT * FROM BNA_FORSALE", conn)
        # Merge new data with existing, keeping only new rows based on zpid (unique property ID)
        if 'zpid' in df.columns and 'zpid' in existing_df.columns:
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['zpid'], keep='last')
    except:
        pass  # Table doesn't exist yet, will create it

    # Convert dict/list to JSON strings for SQLite
    df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

    df.to_sql(name='BNA_FORSALE', con=conn, if_exists='replace', index=False)

    conn.close()

def updateRentalsTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = rentalPipe01().copy()

    # Skip if no data was fetched
    if df.empty:
        print("Skipping BNA_RENTALS table update - no data available")
        conn.close()
        return

    # Read existing data
    try:
        existing_df = pd.read_sql_query("SELECT * FROM BNA_RENTALS", conn)
        # Merge new data with existing, keeping only new rows based on zpid (unique property ID)
        if 'zpid' in df.columns and 'zpid' in existing_df.columns:
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['zpid'], keep='last')
    except:
        pass  # Table doesn't exist yet, will create it

    # Convert dict/list to JSON strings for SQLite
    df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

    df.to_sql(name='BNA_RENTALS', con=conn, if_exists='replace', index=False)

    conn.close()

def updateFredMetricsTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = fredMetricsPipe01().copy()

    # Skip if no data was fetched
    if df.empty:
        print("Skipping BNA_FRED_METRICS table update - no data available")
        conn.close()
        return

    # Convert date column to string for SQLite compatibility
    if 'date' in df.columns:
        df['date'] = df['date'].astype(str)

    # Read existing data
    try:
        existing_df = pd.read_sql_query("SELECT * FROM BNA_FRED_METRICS", conn)
        # Merge and deduplicate based on date + series_id
        df = pd.concat([existing_df, df]).drop_duplicates(
            subset=['date', 'series_id'], keep='last'
        )
    except:
        pass  # Table doesn't exist yet, will create it

    df.to_sql(name='BNA_FRED_METRICS', con=conn, if_exists='replace', index=False)

    conn.close()
    print(f"Successfully updated BNA_FRED_METRICS table with {len(df)} total records")

# Uncomment to run
updateRentalsTable()
updateSalesTable()
updateFredMetricsTable()