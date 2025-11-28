from pipelines.rentalPipe import rentalPipe01
from fredapi import Fred
import folium
import pandas as pd
import requests
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

fred_api_key = os.getenv("FRED_API_KEY")

rental_map_df = rentalPipe01()

# Map variables - TODO: create GeoJson file
rent_long = rental_map_df["longitude"]
rent_lat = rental_map_df["latitude"]
address = rental_map_df["address"]
list_rent_price = rental_map_df["price"]

# Initialize FRED API client
# TODO: Replace 'your_api_key_here' with actual FRED API key or use environment variable
fred = Fred(api_key='your_api_key_here')

# FRED series IDs for Nashville MSA economic indicators
Active_listings = fred.get_series('ACTLISCOU34980')
Median_Price = fred.get_series('MEDLISPRI34980')
Median_dom = fred.get_series('MEDDAYONMAR34980')
Employment_non_farm = fred.get_series('NASH947NA')
msa_population = fred.get_series('NVLPOP')
median_pp_sqft = fred.get_series('MEDLISPRIPERSQUFEE34980')
median_listing_price_change = fred.get_series('MEDLISPRIMM47037')
msa_per_capita_income = fred.get_series('NASH947PCPI')

