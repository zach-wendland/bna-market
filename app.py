import sqlite3
import pandas as pd
import json
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01

def updateSalesTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = forSalePipe01().copy()

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

# Uncomment to run
updateRentalsTable()  
updateSalesTable()