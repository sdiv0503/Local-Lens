import requests
from bs4 import BeautifulSoup
import json
import time

# A new, verified list of 50 recipes from Food.com
URLS = [
    "https://www.food.com/recipe/worlds-best-lasagna-28123",
    "https://www.food.com/recipe/our-favorite-chili-6684",
    "https://www.food.com/recipe/simple-white-cake-12168",
    "https://www.food.com/recipe/classic-guacamole-31605",
    "https://www.food.com/recipe/southern-style-collard-greens-33433",
    "https://www.food.com/recipe/chicken-parmesan-83018",
    "https://www.food.com/recipe/the-best-parmesan-chicken-bake-165030",
    "https://www.food.com/recipe/marinated-grilled-pork-tenderloin-39493",
    "https://www.food.com/recipe/air-fryer-french-fries-533461",
    "https://www.food.com/recipe/chicken-tikka-masala-23746",
    "https://www.food.com/recipe/perfect-prime-rib-28373",
    "https://www.food.com/recipe/salsa-chicken-16954",
    "https://www.food.com/recipe/black-bean-and-corn-salsa-22161",
    "https://www.food.com/recipe/oven-roasted-brussels-sprouts-142340",
    "https://www.food.com/recipe/shrimp-scampi-with-pasta-17056",
    "https://www.food.com/recipe/slow-cooker-pulled-pork-24520",
    "https://www.food.com/recipe/creamy-mushroom-soup-26786",
    "https://www.food.com/recipe/easy-meatballs-75054",
    "https://www.food.com/recipe/the-best-easy-beef-broccoli-stir-fry-296538",
    "https://www.food.com/recipe/the-ultimate-greek-salad-41136",
    "https://www.food.com/recipe/easy-stovetop-macaroni-n-cheese-42976",
    "https://www.food.com/recipe/bevs-spaghetti-sauce-1181",
    "https://www.food.com/recipe/perfect-southern-fried-chicken-14403",
    "https://www.food.com/recipe/chicken-fried-rice-31120",
    "https://www.food.com/recipe/sloppy-joes-118331",
    "https://www.food.com/recipe/leftover-mashed-potato-pancakes-35639",
    "https://www.food.com/recipe/simple-pasta-toss-164741",
    "https://www.food.com/recipe/scalloped-potatoes-34676",
    "https://www.food.com/recipe/jo-mamas-world-famous-spaghetti-32793",
    "https://www.food.com/recipe/turkey-meatloaf-33069",
    "https://www.food.com/recipe/mexican-rice-1132",
    "https://www.food.com/recipe/pizza-meatloaf-cups-211477",
    "https://www.food.com/recipe/stovetop-tuna-casserole-130198",
    "https://www.food.com/recipe/perfect-basic-white-rice-23423",
    "https://www.food.com/recipe/perfect-rump-roast-75416",
    "https://www.food.com/recipe/japanese-mums-chicken-74748",
    "https://www.food.com/recipe/famous-challah-14110",
    "https://www.food.com/recipe/bananas-foster-16382",
    "https://www.food.com/recipe/the-best-snickerdoodles-382",
    "https://www.food.com/recipe/cream-cheese-brownies-43540",
    "https://www.food.com/recipe/strawberry-pie-26330",
    "https://www.food.com/recipe/extra-chocolate-bundt-cake-with-chocolate-glaze-129663",
    "https://www.food.com/recipe/mexican-wedding-cookies-12347",
    "https://www.food.com/recipe/homemade-yellow-cake-32943",
    "https://www.food.com/recipe/barefoot-contessas-carrot-cake-cupcakes-312211",
    "https://www.food.com/recipe/fried-oreos-201552",
    "https://www.food.com/recipe/banana-bread-brownies-460492",
    "https://www.food.com/recipe/boston-cream-pie-20063",
    "https://www.food.com/recipe/peach-cobbler-dump-cake-119131",
    "https://www.food.com/recipe/peanut-butter-cookies-39213"
]

output_filename = "raw_ingredients.txt"

# We still need headers to look like a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Starting recipe scrape for {len(URLS)} recipes from Food.com...")

# "w" means "write" (it will overwrite the file)
with open(output_filename, "w", encoding="utf-8") as f:
    successful_scrapes = 0
    failed_scrapes = 0
    
    for url in URLS:
        print(f"Scraping: {url}")
        
        try:
            # 1. Get the page with our headers
            page = requests.get(url, headers=headers)
            page.raise_for_status() # Check for errors (like 404s)

            soup = BeautifulSoup(page.content, "html.parser")

            # 2. Find the JSON-LD script tag (this is the hidden data)
            script_tag = soup.find("script", type="application/ld+json")
            
            if not script_tag:
                print(f"Warning: Could not find schema JSON for {url}. Skipping.")
                failed_scrapes += 1
                continue

            # 3. Load the script's content as a JSON object
            data = json.loads(script_tag.string)

            # 4. Find the 'Recipe' data
            recipe_data = None
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Recipe":
                        recipe_data = item
                        break
            elif isinstance(data, dict) and data.get("@type") == "Recipe":
                recipe_data = data
            
            if not recipe_data or "recipeIngredient" not in recipe_data:
                print(f"Warning: Found JSON but no 'recipeIngredient' key in {url}. Skipping.")
                failed_scrapes += 1
                continue

            # 5. Get the ingredient list
            ingredients = recipe_data["recipeIngredient"]
            
            print(f"Found {len(ingredients)} ingredients.")
            for ingredient_string in ingredients:
                f.write(ingredient_string + "\n")
            
            successful_scrapes += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            failed_scrapes += 1
        except json.JSONDecodeError:
            print(f"Error parsing JSON from {url}.")
            failed_scrapes += 1
        except Exception as e:
            print(f"An unexpected error occurred for {url}: {e}")
            failed_scrapes += 1
        
        # Be polite to their server
        time.sleep(1)

print("\n--- Scrape Complete ---")
print(f"Successfully scraped {successful_scrapes} recipes.")
print(f"Failed to scrape {failed_scrapes} recipes.")
print(f"All ingredients saved to {output_filename}")