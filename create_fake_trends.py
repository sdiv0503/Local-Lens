import pandas as pd
import numpy as np

print("Generating fake trend data based on robust product list...")

# --- A new keyword list based on your products.csv ---
KEYWORDS = [
    # Trendy Items
    'Avocado', 'Oat Milk', 'Quinoa', 'Greek Yogurt', 'Sourdough Bread', 'Almond Flour',
    
    # Summer Seasonal
    'Vanilla Ice Cream', 'Barbecue Sauce', 'Hot Sauce', 'Hamburger Buns', 'Watermelon', # Assuming Watermelon for summer
    
    # Winter/Holiday Seasonal
    'Turkey Breast', 'Cranberry Sauce', 'Cocoa Powder', 'Sweet Potato', 'Pumpkin Spice', # Adding Pumpkin Spice as a classic example
    
    # Staples (will get generic seasonality)
    'Chicken Breasts', 'Ground Beef', 'Spinach', 'Tomatoes', 'Onion', 
    'Garlic', 'Potatoes', 'Olive Oil', 'Ketchup', 'Mayonnaise', 
    'Spaghetti', 'Diced Tomatoes', 'Salmon', 'Butter', 'White Rice'
]

# Create a 5-year date range (weekly)
dates = pd.date_range(end=pd.Timestamp.today(), periods=261, freq='W-SUN') # 261 weeks = 5 years

all_trends_df = pd.DataFrame()

print(f"Generating trends for {len(KEYWORDS)} keywords...")

for keyword in KEYWORDS:
    # Create a base trend with some random noise
    base_interest = np.random.rand() * 20 + 10  # Base interest between 10 and 30
    base = np.random.rand(len(dates)) * 15 + base_interest  # Base interest with some variation
    noise = np.random.normal(0, 3, len(dates))
    
    # --- Smart Seasonality & Trend Logic ---
    day_of_year = dates.dayofyear
    
    if keyword in ['Avocado', 'Oat Milk', 'Quinoa', 'Greek Yogurt', 'Sourdough Bread', 'Almond Flour']:
        # "Trendy" item: create a steady upward trend over 5 years
        trend_line = np.linspace(0, 40, len(dates)) # Starts low, gets popular
        seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / 365.25) + 1) * 5 # Mild seasonality
        interest = base + trend_line + seasonality + noise
        
    elif keyword in ['Vanilla Ice Cream', 'Barbecue Sauce', 'Hot Sauce', 'Hamburger Buns', 'Watermelon']:
        # "Summer" item: Big spike in June-August (day 150-240)
        seasonality = (np.sin(2 * np.pi * (day_of_year - 180) / 365.25) + 1) * 30 # Spike around day 180 (July)
        interest = base + seasonality + noise

    elif keyword in ['Turkey Breast', 'Cranberry Sauce', 'Sweet Potato', 'Pumpkin Spice']:
        # "Holiday" item: Big spike in Oct-Dec (day 270-365)
        seasonality = (np.sin(2 * np.pi * (day_of_year - 320) / 365.25) + 1) * 35 # Spike around day 320 (Nov)
        interest = base + seasonality + noise

    elif keyword == 'Cocoa Powder':
        # "Winter" item: Higher in cold months
        seasonality = (-np.sin(2 * np.pi * (day_of_year - 180) / 365.25) + 1) * 20 # Inverse of summer spike
        interest = base + seasonality + noise
        
    else:
        # "Staple" item: Generic, mild seasonality
        seasonality = (np.sin(2 * np.pi * (day_of_year - 90) / 365.25) + 1) * 10
        interest = base + seasonality + noise
    
    # Combine and make sure interest is between 0 and 100
    interest = np.clip(interest, 0, 100).astype(int)
    
    # Create the DataFrame
    df = pd.DataFrame({
        'date': dates,
        'interest': interest,
        'keyword': keyword
    })
    
    all_trends_df = pd.concat([all_trends_df, df], ignore_index=True)

# Save to the CSV file
all_trends_df['date'] = all_trends_df['date'].dt.strftime('%Y-%m-%d') # <-- ADD THIS LINE
all_trends_df.to_csv("google_trends_data.csv", index=False)

print("\n--- Success! ---")
print("Generated 'google_trends_data.csv' with fake, realistic data.")
print("New keywords include trendy items (Oat Milk) and seasonal items (Turkey Breast).")
print(all_trends_df.head())