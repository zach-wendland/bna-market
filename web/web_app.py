import sqlite3
from flask import Flask, render_template

app = Flask(__name__, static_folder="static")
DB_PATH = "BNASFR02.db"

def query_all(table):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(f"SELECT * FROM {table}").fetchall()
    con.close()
    return rows


@app.route("/")
def index():
    data1 = query_all("BNA_FORSALE")
    data2 = query_all("BNA_RENTALS")
    return render_template("index.html", data1=data1, data2=data2)


@app.route("/BNA_FORSALE")
def dataset1_partial():
    data1 = query_all("BNA_FORSALE")
    return render_template("_dataset1.html", data1=data1)


@app.route("/BNA_RENTALS")
def dataset2_partial():
    data2 = query_all("BNA_RENTALS")
    return render_template("_dataset2.html", data2=data2)


if __name__ == "__main__":
    app.run(debug=True)
