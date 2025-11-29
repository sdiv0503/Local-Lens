import requests
import pandas as pd

print("Starting product scrape...")

products_list = []
for i in range(2, 12): # This loops from 1 to 5

    # --- THIS IS THE FIX ---
    # We get the JSON data endpoint instead of the HTML page
    URL = f"https://world.openfoodfacts.org/{i}.json"
    print(f"Scraping page {i}: {URL}")

    try:
        # 1. Send the request
        page = requests.get(URL)
        page.raise_for_status() # This will raise an error if the page request fails

        # 2. Parse the JSON data
        # .json() is a built-in requests method
        data = page.json()

        # 3. Check if the 'products' key exists
        if "products" in data:
            
            # 4. Loop through each product in the 'products' list
            for product in data["products"]:
                
                # 5. Extract the data by key
                # We use .get() to avoid errors if a key is missing
                product_name = product.get("product_name", "Unknown Name")
                
                # The categories are in a single string, e.g., "Snacks, Sweet snacks"
                product_category = product.get("categories", "Uncategorized")

                # Handle cases where product_name might be an empty string
                if not product_name:
                    product_name = "Unknown Name"

                # 6. Add our findings to our master list
                products_list.append({
                    "name": product_name,
                    "category": product_category
                })
        else:
            print(f"Warning: 'products' key not found on page {i}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page {i}: {e}")
    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding JSON from page {i}. The page might be empty or not valid JSON.")


# 7. Save to a CSV file
df = pd.DataFrame(products_list)
df.to_csv("products.csv", index=False)

print(f"Done! Scraped {len(df)} products and saved to products.csv")