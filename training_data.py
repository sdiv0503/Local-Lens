TRAIN_DATA = [
    # === Problem 1: Handling "box", "package", and instructions ===
    ("1 box seasoned stuffing mix, prepared as directed (Stove Top, etc.)", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 27, "INGREDIENT")]}),
    ("1 box frozen chopped spinach, thawed and completely drained of all liquid", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 27, "INGREDIENT")]}),
    ("1 (8 ounce) package cream cheese (you can use light)", {"entities": [(0, 1, "QTY"), (2, 17, "UNIT"), (18, 30, "INGREDIENT")]}),
    ("1 package dry hidden valley ranch original ranch dressing mix (not the dip stuff)", {"entities": [(0, 1, "QTY"), (2, 9, "UNIT"), (10, 60, "INGREDIENT")]}),
    ("1 (21 1/2 ounce) package fudge brownie mix", {"entities": [(0, 1, "QTY"), (2, 19, "UNIT"), (20, 37, "INGREDIENT")]}),
    ("1 (8 ounce) can refrigerated crescent dinner rolls", {"entities": [(0, 1, "QTY"), (2, 17, "UNIT"), (18, 51, "INGREDIENT")]}),
    ("1 (14 ounce) can sweetened condensed milk", {"entities": [(0, 1, "QTY"), (2, 17, "UNIT"), (18, 43, "INGREDIENT")]}),
    ("1 (10 ounce) jar plum jelly", {"entities": [(0, 1, "QTY"), (2, 17, "UNIT"), (18, 28, "INGREDIENT")]}),
    ("1 (3 1/2 ounce) box instant vanilla flavor pudding and pie filling", {"entities": [(0, 1, "QTY"), (2, 23, "UNIT"), (24, 66, "INGREDIENT")]}),
    ("1 (16 ounce) can whole tomatoes, undrained and chopped", {"entities": [(0, 1, "QTY"), (2, 17, "UNIT"), (18, 32, "INGREDIENT")]}),

    # === Problem 2: Ignoring preparation (chopped, minced, beaten) ===
    ("1 large egg, beaten", {"entities": [(0, 1, "QTY"), (2, 10, "INGREDIENT")]}),
    ("2 large eggs, Hard Cooked", {"entities": [(0, 1, "QTY"), (2, 11, "INGREDIENT")]}),
    ("2 garlic cloves, finely minced (or crushed)", {"entities": [(0, 1, "QTY"), (2, 15, "INGREDIENT")]}),
    ("1 small onion, diced", {"entities": [(0, 1, "QTY"), (2, 13, "INGREDIENT")]}),
    ("1 cup butter, softened", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 12, "INGREDIENT")]}),
    ("1/2 lb shrimp, deveined", {"entities": [(0, 3, "QTY"), (4, 6, "UNIT"), (7, 13, "INGREDIENT")]}),
    ("1 lb uncooked shrimp, peeled and deveined", {"entities": [(0, 1, "QTY"), (2, 4, "UNIT"), (5, 20, "INGREDIENT")]}),
    ("1 cup chopped onion", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 20, "INGREDIENT")]}),
    ("1/2 cup chopped onion", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 22, "INGREDIENT")]}),
    ("2 large tomatoes, peeled,seeded and chopped", {"entities": [(0, 1, "QTY"), (2, 16, "INGREDIENT")]}),

    # === Problem 3: Basic QTY / UNIT / INGREDIENT ===
    ("1/2 cup mayonnaise", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 18, "INGREDIENT")]}),
    ("1 dash celery salt", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 18, "INGREDIENT")]}),
    ("1 dash onion salt", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 17, "INGREDIENT")]}),
    ("1 dash garlic powder", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 20, "INGREDIENT")]}),
    ("1/2 cup oat bran", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 16, "INGREDIENT")]}),
    ("1/3 cup sugar", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 13, "INGREDIENT")]}),
    ("2 teaspoons vanilla", {"entities": [(0, 1, "QTY"), (2, 11, "UNIT"), (12, 19, "INGREDIENT")]}),
    ("2 cups all-purpose flour", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 26, "INGREDIENT")]}),
    ("1/3 cup cocoa", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 13, "INGREDIENT")]}),
    ("1 teaspoon baking soda", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 22, "INGREDIENT")]}),
    ("1/2 teaspoon salt", {"entities": [(0, 3, "QTY"), (4, 12, "UNIT"), (13, 17, "INGREDIENT")]}),
    ("3 tablespoons honey", {"entities": [(0, 1, "QTY"), (2, 13, "UNIT"), (14, 19, "INGREDIENT")]}),
    ("1 tablespoon sesame seeds", {"entities": [(0, 1, "QTY"), (2, 12, "UNIT"), (13, 25, "INGREDIENT")]}),
    ("1 teaspoon cornstarch", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 21, "INGREDIENT")]}),
    ("1/3 cup buttermilk", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 18, "INGREDIENT")]}),
    ("1 teaspoon fresh dill", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 21, "INGREDIENT")]}),
    ("1 teaspoon fresh parsley", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 24, "INGREDIENT")]}),
    ("1/2 teaspoon vinegar", {"entities": [(0, 3, "QTY"), (4, 12, "UNIT"), (13, 20, "INGREDIENT")]}),
    ("1 teaspoon active dry yeast", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 28, "INGREDIENT")]}),
    ("3 cups bread flour", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 18, "INGREDIENT")]}),
    ("1 tablespoon olive oil", {"entities": [(0, 1, "QTY"), (2, 12, "UNIT"), (13, 22, "INGREDIENT")]}),
    ("2 tablespoons melted butter", {"entities": [(0, 1, "QTY"), (2, 13, "UNIT"), (14, 28, "INGREDIENT")]}),
    ("2 tablespoons balsamic vinegar", {"entities": [(0, 1, "QTY"), (2, 13, "UNIT"), (14, 30, "INGREDIENT")]}),
    ("2 tablespoons extra virgin olive oil", {"entities": [(0, 1, "QTY"), (2, 13, "UNIT"), (14, 36, "INGREDIENT")]}),
    ("1/4 teaspoon ground black pepper", {"entities": [(0, 3, "QTY"), (4, 12, "UNIT"), (13, 32, "INGREDIENT")]}),
    ("2 lbs boneless skinless chicken breasts", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 40, "INGREDIENT")]}),
    ("1/2 cup water", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 13, "INGREDIENT")]}),
    ("1/2 cup oil", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 11, "INGREDIENT")]}),
    ("1 egg", {"entities": [(0, 1, "QTY"), (2, 5, "INGREDIENT")]}),
    ("1/2 cup semi-sweet chocolate chips", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 34, "INGREDIENT")]}),
    ("1 cup orange juice", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 18, "INGREDIENT")]}),
    ("1 cup rice", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 10, "INGREDIENT")]}),

    # === Problem 4: Handling quantity ranges ===
    ("1/4-1/2 cup margarine", {"entities": [(0, 7, "QTY"), (8, 11, "UNIT"), (12, 21, "INGREDIENT")]}),
    ("1 -2 tablespoon your favorite hot sauce (adjust to taste)", {"entities": [(0, 4, "QTY"), (5, 15, "UNIT"), (16, 37, "INGREDIENT")]}),
    ("6 -8 new potatoes, cut in 1 inch pieces", {"entities": [(0, 4, "QTY"), (5, 40, "INGREDIENT")]}),
    ("5 -6 cloves garlic, minced", {"entities": [(0, 4, "QTY"), (5, 26, "INGREDIENT")]}),

    # === Problem 5: Handling complex parentheticals ===
    ("1/2 cup egg white (3 to 4 medium)", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 17, "INGREDIENT")]}),
    ("1 1/4 cups lukewarm water (105 to 115 F)", {"entities": [(0, 5, "QTY"), (6, 10, "UNIT"), (11, 25, "INGREDIENT")]}),
    ("6 cups cooked black beans (, 3 15-oz cans, rinsed and drained)", {"entities": [(0, 1, "QTY"), (2, 6, "UNIT"), (7, 24, "INGREDIENT")]}),
    
    # === Problem 6: Handling "or" lines (by choosing one side) ===
    # We teach the model that "margarine" is the ingredient, not the full string.
    ("1/2 cup margarine or 1/2 cup butter, softened", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 17, "INGREDIENT")]}),
    # We teach it that "green olives" is the ingredient.
    ("1/3 cup green olives or 1/3 cup vegetable oil", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (8, 20, "INGREDIENT")]}),
    
    # === Problem 7: Handling simple, no-quantity/unit ingredients ===
    ("fresh ground pepper", {"entities": [(0, 19, "INGREDIENT")]}),
    ("Crisco (for greasing pans)", {"entities": [(0, 6, "INGREDIENT")]}),
    ("colored decorating sugar", {"entities": [(0, 24, "INGREDIENT")]}),
    ("black pepper", {"entities": [(0, 12, "INGREDIENT")]}),
    ("minced fresh cilantro (optional)", {"entities": [(0, 21, "INGREDIENT")]}),
    ("salt", {"entities": [(0, 4, "INGREDIENT")]}),
    ("nonstick cooking spray", {"entities": [(0, 22, "INGREDIENT")]}),
    ("flaked coconut", {"entities": [(0, 14, "INGREDIENT")]}),
    ("Mountain Dew soda", {"entities": [(0, 17, "INGREDIENT")]}),
    ("ice cube", {"entities": [(0, 8, "INGREDIENT")]}),
    
    # === Problem 8: Handling problematic lines from your screenshot ===
    # This teaches it that "Dijon mustard" is the ingredient.
    ("1 teaspoon Dijon mustard", {"entities": [(0, 1, "QTY"), (2, 10, "UNIT"), (11, 25, "INGREDIENT")]}), 
    # This teaches it "parmesan cheese" is the ingredient, ignoring "grated"
    ("1/2 cup freshly grated parmesan cheese", {"entities": [(0, 3, "QTY"), (4, 7, "UNIT"), (16, 31, "INGREDIENT")]}), 
    # This teaches it "romano cheese" is the ingredient.
    ("1 cup romano cheese", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 19, "INGREDIENT")]}), # I added this line based on your problem.
    # This teaches it "seasoned stuffing mix" is the ingredient.
    ("1 box seasoned stuffing mix", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 27, "INGREDIENT")]}), # I added this simple version.
    # This teaches it "frozen chopped spinach" is the ingredient.
    ("1 box frozen chopped spinach", {"entities": [(0, 1, "QTY"), (2, 5, "UNIT"), (6, 27, "INGREDIENT")]}), # I added this simple version.
]