import spacy

# 1. Load our saved, custom model from the folder
print("Loading custom model from './my_ingredient_model'...")
nlp = spacy.load("./my_ingredient_model")

# 2. Let's test it on our new, "tough" unseen strings
print("\n--- Testing Model on Tough Examples ---")
TOUGH_TEST_STRINGS = [
    # Non-ingredient text (should find nothing)
    "Preheat oven to 350 degrees F",
    # Standard text
    "1 1/2 cups all-purpose flour",
    # Text with word-based QTY
    "one large onion, finely chopped",
    # Text with complex QTY/UNIT
    "1 (16 ounce) package of cream cheese",
    # Text with no QTY/UNIT
    "salt and pepper to taste",
    # Text with "a" as QTY
    "a pinch of saffron",
    # Text with punctuation in UNIT
    "2 tbsp. baking soda"
]

for text in TOUGH_TEST_STRINGS:
    # 3. Run the text through our model's pipeline
    doc = nlp(text)

    # 4. Print the "doc.ents" (the entities it found)
    print(f"\nText: '{text}'")
    print("Entities:")
    if not doc.ents:
        print("  (No entities found)")

    for ent in doc.ents:
        # ent.label_ is the "LABEL" (QTY, UNIT, etc.)
        # ent.text is the actual text it found
        print(f"  {ent.label_:<12} | {ent.text}")

print("\n--- Test Complete ---")
print("Review the entities above. They should match what you saw in the HTML file.")
