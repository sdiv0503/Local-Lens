import spacy
from spacy.scorer import Scorer
from spacy.training import Example
from spacy.displacy import render
from spacy.tokens import Doc
from pathlib import Path

# --- 1. DEFINE YOUR "GOLD STANDARD" TEST SET ---
# This time, we define the answers with start/end indices that
# are *guaranteed* to be correct.
GOLD_STANDARD_TEST_DATA = [
    (
        "Preheat oven to 350 degrees F",
        {"entities": []}
    ),
    (
        "3 large eggs, lightly beaten",
        {"entities": [(0, 1, "QTY"), (2, 29, "INGREDIENT")]}
    ),
    (
        "1 1/2 cups all-purpose flour",
        {"entities": [(0, 5, "QTY"), (6, 10, "UNIT"), (11, 28, "INGREDIENT")]}
    ),
    (
        "one large onion, finely chopped",
        {"entities": [(0, 3, "QTY"), (4, 32, "INGREDIENT")]}
    ),
    (
        "1 (16 ounce) package of cream cheese",
        {"entities": [(0, 1, "QTY"), (14, 21, "UNIT"), (25, 37, "INGREDIENT")]}
    ),
    (
        "salt and pepper to taste",
        {"entities": [(0, 25, "INGREDIENT")]}
    ),
    (
        "a pinch of saffron",
        {"entities": [(0, 1, "QTY"), (2, 7, "UNIT"), (11, 18, "INGREDIENT")]}
    ),
    (
        "2 tbsp. baking soda",
        {"entities": [(0, 1, "QTY"), (2, 7, "UNIT"), (8, 20, "INGREDIENT")]}
    )
]

# --- 2. LOAD YOUR TRAINED MODEL ---
print("Loading custom model from './my_ingredient_model'...")
model_path = "./my_ingredient_model"
nlp = spacy.load(model_path)

# --- 3. CALCULATE PERFORMANCE METRICS (NEW ROBUST WAY) ---
print("Calculating model performance...")
scorer = Scorer()
examples = []
all_docs_to_visualize = []

for text, annotations in GOLD_STANDARD_TEST_DATA:
    
    # Run the text through the trained model to get the PREDICTION
    predicted_doc = nlp(text)
    all_docs_to_visualize.append(predicted_doc) # Add for visualization
    
    # Create the "gold standard" REFERENCE doc
    reference_doc = nlp.make_doc(text)
    ents = []
    for start, end, label in annotations["entities"]:
        span = reference_doc.char_span(start, end, label=label, alignment_mode="contract")
        
        if span is None:
            # This is our own, better error message
            print(f"--- !!! ERROR IN TEST DATA !!! ---")
            print(f"Could not create span for: {(start, end, label)} in '{text}'")
            print("This test example will be SKIPPED. Fix the indices above.")
            print(f"------------------------------------")
        else:
            ents.append(span)
            
    reference_doc.ents = ents
    
    # Create the Example object and add it to our list
    example = Example(predicted_doc, reference_doc)
    examples.append(example)

# Score the list of Examples
scores = scorer.score(examples)

print("\n--- MODEL PERFORMANCE (STRICT) ---")
print(f"Overall Precision (p): {scores['ents_p']:.3f}")
print(f"Overall Recall (r):    {scores['ents_r']:.3f}")
print(f"Overall F1-score (f):  {scores['ents_f']:.3f}")
print("\n--- SCORES BY ENTITY TYPE ---")
if 'ents_per_type' in scores:
    for entity_type, metrics in scores['ents_per_type'].items():
        print(f"  {entity_type}:")
        print(f"    Precision: {metrics['p']:.3f}")
        print(f"    Recall:    {metrics['r']:.3f}")
        print(f"    F1-score:  {metrics['f']:.3f}")
else:
    print("Could not calculate scores per entity type.")


# --- 4. CREATE VISUALIZATION ---
print("\n--- GENERATING VISUALIZATION ---")
output_path = Path("test_visualization.html")

# Render the HTML
html = render(all_docs_to_visualize, style="ent", page=True, 
              options={"colors": {"QTY": "#FFC107", "UNIT": "#4CAF50", "INGREDIENT": "#2196F3"}})

# Save the HTML to a file
output_path.open("w", encoding="utf-8").write(html)

print(f"\nSuccess! Open '{output_path.name}' in your browser to see the model's predictions.")

