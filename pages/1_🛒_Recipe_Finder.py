import streamlit as st
import spacy
import psycopg2
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json # <-- Added for the new scraper

# --- Page Config ---
st.set_page_config(
    page_title="LocalLens",
    page_icon="🛒",
    layout="wide"
)

# --- Database Connection ---
@st.cache_resource
def init_connection():
    try:
        conn = psycopg2.connect(
            dbname="local_lens_db",
            user="postgres",
            password="postgre", 
            host="localhost",
            port="5432"
        )
        print("Database connection successful!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        st.error(f"Database connection failed: {e}")
        return None

# Run the connection function
conn = init_connection()

# --- Load NLP Model ---
@st.cache_resource
def load_nlp_model():
    try:
        nlp = spacy.load("./my_ingredient_model")
        print("NLP model loaded successfully!")
        return nlp
    except OSError:
        print("Error: NLP model not found. Run train_nlp.py first.")
        st.error("NLP model not found. Please train the model first.")
        return None

# Run the model loading function
nlp = load_nlp_model()

# --- Headers for Scraping ---
# We need this to pretend to be a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- App UI ---
st.title("🛒 LocalLens: Your Recipe Ingredient Finder")
st.markdown("""
Welcome! Paste the URL of a recipe from **Food.com** and we'll check our local store inventories for the ingredients.
""")

# Only one text_input box
url = st.text_input(
    "Paste your Food.com recipe URL here:",
    "https://www.food.com/recipe/worlds-best-lasagna-28123" # A working food.com URL
)

# --- Helper Functions (The "Backend" Logic) ---

def scrape_recipe(recipe_url):
    """Scrapes a single Food.com URL for its ingredient list."""
    try:
        page = requests.get(recipe_url, headers=headers)
        page.raise_for_status() # Check for errors (like 404)
        soup = BeautifulSoup(page.content, "html.parser")
        
        # --- This is the new, correct scraping logic for Food.com ---
        script_tag = soup.find("script", type="application/ld+json")
        
        if not script_tag:
            st.error("Could not find recipe data script on this page. Is it a valid Food.com URL?")
            return []

        data = json.loads(script_tag.string)
        
        recipe_data = None
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Recipe":
                    recipe_data = item
                    break
        elif isinstance(data, dict) and data.get("@type") == "Recipe":
            recipe_data = data
        
        if not recipe_data or "recipeIngredient" not in recipe_data:
            st.error("Found recipe data, but couldn't parse the ingredient list.")
            return []
            
        return recipe_data["recipeIngredient"] # This is the list of ingredients
        
    except Exception as e:
        st.error(f"Error scraping URL: {e}")
        return []

def parse_ingredients(ingredient_list):
    """Uses our custom NLP model to parse a list of raw ingredient strings."""
    if nlp is None:
        st.error("NLP model is not loaded.")
        return []
        
    parsed_ingredients = []
    print("--- PARSING INGREDIENTS ---")
    for text in ingredient_list:
        doc = nlp(text) # Run the raw text through our "brain"
        
        main_ingredient = None
        for ent in doc.ents:
            if ent.label_ == "INGREDIENT":
                # Clean up the text a bit
                main_ingredient = ent.text.replace(", chopped", "").replace(", minced", "")
                main_ingredient = main_ingredient.split(",")[0].strip() # Take only the part before the first comma
                break # Take the first one we find
        
        if main_ingredient:
            # Handle simple pluralization for better matching
            if main_ingredient.endswith('s') and not main_ingredient.endswith('ss'):
                 parsed_ingredients.append(main_ingredient[:-1]) # add 'tomato'
            parsed_ingredients.append(main_ingredient) # add 'tomatoes'
        else:
            print(f"Parsed: '{text}' -> No ingredient found.")
            
    # Return a de-duplicated list
    return list(set(parsed_ingredients))

def check_inventory(ingredient_names):
    """Queries the database to find which stores have which ingredients."""
    if conn is None:
        st.error("Database connection is not available.")
        return pd.DataFrame(), pd.DataFrame()

    if not ingredient_names:
        return pd.DataFrame(), pd.DataFrame()

    # --- THIS IS THE NEW, SMARTER LOGIC ---
    # Build a dynamic 'WHERE' clause to do a "fuzzy AND" search.
    # e.g., for "grated parmesan", we search for
    # (name ILIKE '%grated%' AND name ILIKE '%parmesan%')
    
    where_clauses = []
    all_search_terms = []
    
    for ingredient in ingredient_names:
        # Split the ingredient name into individual words
        words = ingredient.split()
        if not words:
            continue
            
        # Create an AND clause for each word
        word_clauses = []
        for word in words:
            # We will pass the 'word' as a parameter to prevent SQL injection
            word_clauses.append("name ILIKE %s")
            # We add the %...% here to the parameter
            all_search_terms.append(f"%{word}%")
        
        # Join the words with "AND"
        # e.g., (name ILIKE %s AND name ILIKE %s)
        where_clauses.append(f"({' AND '.join(word_clauses)})")

    # Join all ingredient clauses with "OR"
    # e.g., (clause1) OR (clause2) OR ...
    if not where_clauses:
        return pd.DataFrame(), ingredient_names # Nothing to search for

    dynamic_where_clause = " OR ".join(where_clauses)
    # --- END OF NEW LOGIC ---

    # We use a SQL "Common Table Expression" (CTE) for a cleaner query
    query = f"""
        WITH FoundProducts AS (
            -- Find all product_ids that *fuzzy match* our ingredient list
            SELECT 
                product_id, 
                name AS product_name
            FROM products
            WHERE 
                {dynamic_where_clause}
        )
        -- Now, check our inventory for those found products
        SELECT 
            s.name AS store_name,
            fp.product_name,
            i.stock_quantity,
            i.price
        FROM inventory i
        JOIN stores s ON i.store_id = s.store_id
        JOIN FoundProducts fp ON i.product_id = fp.product_id
        WHERE i.stock_quantity > 0;
    """
    
    # Execute the query
    # We pass 'all_search_terms' as the parameters
    try:
        df = pd.read_sql_query(query, conn, params=tuple(all_search_terms))
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame(), ingredient_names

    # --- NEW LOGIC FOR MISSING INGREDIENTS ---
    # Now we check which of our *original* ingredients were found
    found_in_db = df['product_name'].unique()
    
    missing_ingredients = []
    for name in ingredient_names:
        # Check if any found product matches all words in the ingredient name
        is_found = False
        for fi in found_in_db:
            words_in_name = name.split()
            if all(word.lower() in fi.lower() for word in words_in_name):
                is_found = True
                break
        if not is_found:
            missing_ingredients.append(name)
    
    return df, missing_ingredients

# --- Button and Main Logic ---

# --- Button and Main Logic ---

if st.button("Find Ingredients"):
    
    # First, check if our critical components are loaded
    if conn is None or nlp is None:
        st.error("Application is not initialized. Please check console logs.")
    else:
        # Use spinners to show loading status
        with st.spinner("Step 1: Scraping recipe..."):
            raw_ingredients = scrape_recipe(url)
        
        with st.spinner("Step 2: Parsing ingredients with NLP..."):
            parsed_ingredients = parse_ingredients(raw_ingredients)
            
            # --- AESTHETIC UPGRADE 1: Better Success Message ---
            st.success(f"Success! We found matches for {len(parsed_ingredients)} ingredients.")
            
            # --- AESTHETIC UPGRADE 2: Bulleted List ---
            st.subheader("📊 We are searching for:")
            markdown_list = ""
            for item in parsed_ingredients:
                markdown_list += f"- {item.capitalize()}\n"
            st.markdown(markdown_list)
        
        with st.spinner("Step 3: Checking store inventories..."):
            inventory_df, missing_from_db = check_inventory(parsed_ingredients)
        
        # --- Display Results ---
        st.subheader("🛒 Shopping List & Store Availability")
        
        if inventory_df.empty:
            st.warning("Sorry, we couldn't find any of these ingredients in our local stores.")
        else:
            # This is the "Solver" Logic from our plan
            store_summary = inventory_df.groupby('store_name')['product_name'].count()
            store_summary = store_summary.to_frame(name="items_found")
            store_summary['items_needed'] = len(parsed_ingredients)
            store_summary['match_pct'] = (store_summary['items_found'] / store_summary['items_needed']) * 100
            store_summary = store_summary.sort_values(by="match_pct", ascending=False)
            
            # This code is already correct, we fixed the min_value/max_value
            st.dataframe(
                store_summary,
                column_config={
                    "items_found": "Items Found",
                    "items_needed": "Total Items",
                    "match_pct": st.column_config.ProgressColumn(
                        "Match %",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100,
                    )
                },
                width="stretch"
            )
            
            st.markdown("---")
            
            # --- AESTHETIC UPGRADE 3: Emojis and Cleaned Tables ---
            st.subheader("🏬 Detailed Breakdown")
            for store_name in store_summary.index:
                with st.expander(f"**{store_name}** ({store_summary.loc[store_name, 'items_found']} items found)"):
                    store_df = inventory_df[inventory_df['store_name'] == store_name]
                    
                    # This is the new, upgraded dataframe call
                    st.dataframe(
                        store_df[['product_name', 'price', 'stock_quantity']], 
                        column_config={
                            "product_name": "Product",
                            "price": st.column_config.NumberColumn(
                                "Price",
                                format="₹%.2f"  # <-- HERE is the Rupee symbol!
                            ),
                            "stock_quantity": "Stock"
                        },
                        hide_index=True,  # <-- Hides the 0, 1, 2, 3...
                        width="stretch"
                    )
        
        # Display ingredients we couldn't find in our DB at all
        if missing_from_db:
            # --- AESTHETIC UPGRADE 4: Cleaner Missing List ---
            st.subheader("❌ Missing from All Stores")
            st.warning("Our database doesn't seem to have products matching:")
            
            missing_markdown = ""
            for item in missing_from_db:
                missing_markdown += f"- {item.capitalize()}\n"
            st.markdown(missing_markdown)