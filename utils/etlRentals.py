"""
NOT FINISHED YET
"""

import pandas as pd
import numpy as np
from pipelines.rentalPipe import rentalPipe01

def cleanRentData(df):
    df = df.reset_index(drop=True)
    df["row_id"] = df.index  # stable fallback key

    exploded = df[["row_id", "units"]].explode("units", ignore_index=True)
   
    parsed = pd.json_normalize(exploded["units"])
    parsed["row_id"] = exploded["row_id"]
    
    
    parsed["price_num"] = (
        parsed["price"]
        .str.replace(r"[^0-9.]", "", regex=True)
        .astype(float)
    )

    parsed["bedrooms"] = (
        parsed["beds"]
        .str.replace(r"[^0-9.]", "", regex=True)
    )
    
    parsed["price_num"]
    parsed['bedrooms']

    
    best = (parsed.sort_values(["row_id", "price_num","bedrooms"])
                .groupby("row_id", as_index=False)
                .first()
                .drop(columns=["price_num", "bedrooms"]))

    
    agg = (parsed.groupby("row_id")
                .apply(lambda g: g[["price","beds"]].to_dict("records"))
                .reset_index(name="units_parsed"))
    
    df_base = df.drop(columns=["units"])   # drop nested original

    df_final = df_base.merge(best, on="row_id", how="left")
    
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    
    df_final["price_y"] = df_final["price_y"].replace("nan", np.nan)
    df_final["price_x"] = df_final["price_x"].replace("nan", np.nan)

    df_final["combined_price"] = df_final["price_y"].fillna(df_final["price_x"])

    
    df_final["bedrooms"] = df_final["bedrooms"].replace("nan", np.nan)
    df_final["beds"] = df_final["beds"].replace("nan", np.nan)

    df_final["combined_beds"] = df_final["bedrooms"].fillna(df_final["beds"])
    
    img_url = df_final['imgSrc']
    detailUrls = df_final['detailUrl']

    #%%
    df_final = df_final.drop(columns=['hasImage','isBuilding','isContactable','isInstantTourEnabled','listingStatus',
                                      'availabilityCount','has3DModel', 'imgSrc', 'comingSoonOnMarketDate', 'contingentListingType',
                                      'country', 'currency', 'hasVideo','listingSubType', 'lotAreaValue','rentZestimate',
                                      'variableData','zestimate','unit','roomForRent', 'lotAreaUnit', 'carouselPhotos',
                                      'detailUrl', 'zpid','price_x','price_y','row_id','lotId'])
    
    return df_final

rent_df = rentalPipe01()

df = cleanRentData(rent_df)

print(df)