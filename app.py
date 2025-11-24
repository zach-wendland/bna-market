import sqlite3
import pandas as pd
import json
from pipelines.forSale import forSalePipe01
from pipelines.rentalPipe import rentalPipe01

def updateSalesTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = forSalePipe01().copy()
    # Convert dict/list to JSON strings for SQLite
    df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

    df.to_sql(name='BNA_FORSALE', con=conn, if_exists='replace', index=False)

    conn.close()

def updateRentalsTable():
    conn = sqlite3.connect('BNASFR02.DB')

    df = rentalPipe01().copy()
    # Convert dict/list to JSON strings for SQLite
    df = df.map(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)

    df.to_sql(name='BNA_RENTALS', con=conn, if_exists='replace', index=False)

    conn.close()

# Uncomment to run
updateRentalsTable()  
updateSalesTable()