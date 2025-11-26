from pipelines.rentalPipe import rentalPipe01
from fredapi import Fred
import Folium
import pandas as pd
import requests 

rental_map_df = rentalPipe01()

# Map variables - TODO: create GeoJson file
rent_long = rental_map_df["longitude"] 
rent_lat = rental_map_df["latitude"]
address = rental_map_df["address"]
list_rent_price = rental_map_d["price"]

# FRED variables
"""
Active_listings =  ACTLISCOU34980
Median_Price =  MEDLISPRI34980
Median_dom =  MEDDAYONMAR34980
Employment_non_farm =  NASH947NA
msa_population =  NVLPOP
median_pp_sqft =  MEDLISPRIPERSQUFEE34980
median_listing_price_change =  MEDLISPRIMM47037
msa_per_capita_income =  NASH947PCPI
"""
