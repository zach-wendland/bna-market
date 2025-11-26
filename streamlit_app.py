import stresmlit as st
from pipelines.rentalPipe import rentalPipe01


rental_map_df = rentalPipe01()

rent_long = rental_map_df["longitude"] 

rent_lat = rental_map_df["latitude"]

st.map()
