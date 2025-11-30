import streamlit as st
import spacy
import pandas as pd
import requests
from bs4 import BeautifulSoup
from db import init_connection  # <--- IMPORT THE SHARED CONNECTION

# --- Page Config ---
st.set_page_config(
    page_title="Recipe Finder",
    page_icon="🛒",
    layout="wide"
)

st.title("🛒 LocalLens: Recipe Ingredient Finder")
st.markdown("""
Paste a recipe URL from **Food.com**, and we'll check which ingredients are in stock at local stores.
""")

# --- Connect to DB (Using Shared Logic) ---
conn = init_connection()

# --- Load NLP Model ---
@st.cache_resource
def load_nlp_model():
    try:
        # Load the custom model from the folder
        nlp = spacy.load("./my_ingredient_model")
        return nlp
    except OSError:
        st.error("NLP model not found. Please ensure 'my_ingredient_model' folder is uploaded.")
        return None

nlp = load_nlp_model()

# --- Helper Functions ---
def scrape_recipe(recipe_url):
    """Scrapes a single Food.com URL for its ingredient list."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get(recipe_url, headers=headers)
        page.raise_for_status()
        soup = BeautifulSoup(page.content, "html.parser")
        
        # Food.com specific scraping logic
        ingredients = []
        # Try finding JSON-LD first (more reliable)
        import json
        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            data = json.loads(script_tag.string)
            if isinstance(data, list):
                data = data[0] # Sometimes it's a list
            if "recipeIngredient" in data:
                return data["recipeIngredient"]

        # Fallback to HTML classes if JSON fails
        ingredient_elements = soup.find_all("div", class_="ingredient-text") # Common class
        if not ingredient_elements:
             ingredient_elements = soup.find_all("li", class_="ingredient") # Another common one

        if not ingredient_elements:
            return []
            
        return [el.get_text(strip=True) for el in ingredient_elements]
        
    except Exception as e:
        st.error(f"Error scraping URL: {e}")
        return []

def parse_ingredients(ingredient_list):
    """Uses our custom NLP model to parse a list of raw ingredient strings."""
    if nlp is None: return []
        
    parsed_ingredients = []
    for text in ingredient_list:
        doc = nlp(text)
        # Extract the *main* ingredient text
        main_ingredient = None
        for ent in doc.ents:
            if ent.label_ == "INGREDIENT":
                main_ingredient = ent.text
                break 
        
        if main_ingredient:
            parsed_ingredients.append(main_ingredient)
            
    return list(set(parsed_ingredients))

def check_inventory(ingredient_names):
    """Queries the database to find which stores have which ingredients."""
    if conn is None:
        st.error("Database connection is not available.")
        return pd.DataFrame(), []

    if not ingredient_names:
        return pd.DataFrame(), []

    # Build Dynamic Query for "Fuzzy Matching"
    where_clauses = []
    all_search_terms = []
    
    for ingredient in ingredient_names:
        words = ingredient.split()
        if not words: continue
        word_clauses = []
        for word in words:
            word_clauses.append("name ILIKE %s")
            all_search_terms.append(f"%{word}%")
        where_clauses.append(f"({' AND '.join(word_clauses)})")

    if not where_clauses:
        return pd.DataFrame(), ingredient_names

    dynamic_where_clause = " OR ".join(where_clauses)

    query = f"""
        WITH FoundProducts AS (
            SELECT product_id, name AS product_name
            FROM products
            WHERE {dynamic_where_clause}
        )
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
    
    try:
        df = pd.read_sql(query, conn, params=tuple(all_search_terms))
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame(), ingredient_names

    # Check for missing items
    found_in_db = df['product_name'].unique()
    missing_ingredients = []
    for name in ingredient_names:
        is_found = False
        for fi in found_in_db:
            if all(word.lower() in fi.lower() for word in name.split()):
                is_found = True
                break
        if not is_found:
            missing_ingredients.append(name)
    
    return df, missing_ingredients

# --- Main UI Logic ---
url = st.text_input("Paste Recipe URL:", "https://www.food.com/recipe/worlds-best-lasagna-28123")

if st.button("Find Ingredients"):
    if conn is None or nlp is None:
        st.error("System not initialized.")
    else:
        with st.spinner("Scraping recipe..."):
            raw_ingredients = scrape_recipe(url)
        
        if not raw_ingredients:
            st.error("Could not find ingredients on this page. Try a different Food.com URL.")
        else:
            with st.spinner("Parsing ingredients (AI)..."):
                parsed_ingredients = parse_ingredients(raw_ingredients)
                
                # Aesthetic List
                st.subheader("📝 Shopping List")
                st.markdown(", ".join([f"**{i}**" for i in parsed_ingredients]))
            
            with st.spinner("Checking local stores..."):
                inventory_df, missing = check_inventory(parsed_ingredients)
                
            st.divider()
            
            if inventory_df.empty:
                st.warning("No ingredients found in local stores.")
            else:
                st.header("🏪 Store Availability")
                
                # Summary Table
                summary = inventory_df.groupby('store_name')['product_name'].count().reset_index()
                summary.columns = ['Store', 'Items Found']
                summary['Total Needed'] = len(parsed_ingredients)
                summary['Match %'] = (summary['Items Found'] / len(parsed_ingredients)) * 100
                summary = summary.sort_values('Match %', ascending=False)
                
                st.dataframe(
                    summary,
                    hide_index=True,
                    column_config={
                        "Match %": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100)
                    },
                    use_container_width=True
                )
                
                # Detailed Breakdown
                for _, row in summary.iterrows():
                    store = row['Store']
                    with st.expander(f"📦 {store} ({row['Items Found']} items)"):
                        store_items = inventory_df[inventory_df['store_name'] == store]
                        st.dataframe(
                            store_items[['product_name', 'price', 'stock_quantity']],
                            hide_index=True,
                            column_config={
                                "product_name": "Product",
                                "price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                                "stock_quantity": "Stock"
                            },
                            use_container_width=True
                        )

            if missing:
                st.divider()
                st.error(f"❌ Missing Items ({len(missing)})")
                st.caption("We couldn't find these in any local store database:")
                st.markdown(", ".join(missing))