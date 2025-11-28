import requests
import pandas as pd
import json
import time 
from dotenv import load_dotenv
import os

load_dotenv()

def forSalePipe01() -> pd.DataFrame:
    url = "https://zillow-com1.p.rapidapi.com/propertyByPolygon"
    polygon_coords = "-87.2316 36.5227, -86.3316 36.5227, -86.3316 35.8027, -87.2316 35.8027, -87.2316 36.5227"

    base_querystring = { 
        "polygon": polygon_coords,
        "status_type": "ForSale",
        "minPrice": "100000",
        "maxPrice": "700000",
        "bathsMin": "1", "bathsMax": "4",
        "bedsMin": "1", "bedsMax": "5",
        "sqftMin": "700", "sqftMax": "5000",
        "buildYearMin": "1990"
    }

    headers = {
        "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
    }

    # pagination logic
    all_properties = [] # collects data from pages
    current_page = 1
    max_pages_to_fetch = 20 # max 20

    # iterate over data
    while current_page <= max_pages_to_fetch:
        querystring = base_querystring.copy()

        querystring['page'] = current_page

        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()

            full_response_data = response.json()
            page_properties = full_response_data.get('props', [])


            all_properties.extend(page_properties)

            current_page += 1
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            print(f"API request failed on page {current_page}: {e}")
            break 
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from response on page {current_page}. Content: {response.text}")
            break 
        except Exception as e:
            print(f"An unexpected error occurred on page {current_page}: {e}")
            break 

    df = pd.DataFrame()  # Ensure df is always defined
    if all_properties:
        df = pd.DataFrame(all_properties)
        print(f"Total properties collected: {len(all_properties)}")
        # print(df.head())  # Uncomment for debugging
        print(f"\nDataFrame shape: {df.shape}")
    else:
        print("\nNo properties were collected from any page to create a DataFrame.")
    # df.to_csv("test1.csv")
    return df