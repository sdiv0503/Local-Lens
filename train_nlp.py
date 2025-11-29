import spacy
import random
from spacy.util import minibatch, compounding
from spacy.training import Example

# 1. Import our hard-earned labeled data
try:
    from training_data import TRAIN_DATA
except ImportError:
    print("Error: training_data.py not found or is empty.")
    print("Please create it and add your labeled data first.")
    exit()

if not TRAIN_DATA:
    print("Error: TRAIN_DATA list in training_data.py is empty.")
    print("Please add at least 20-30 labeled examples.")
    exit()

def main(n_iter=30, model_dir="./my_ingredient_model"):
    """Main function to train the custom NER model."""

    # 2. Create a blank English "nlp" object
    nlp = spacy.blank("en")
    print("Created blank 'en' model")

    # 3. Create the "ner" (Named Entity Recognition)
    # pipeline component and add it to the pipeline
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")

    # 4. Add our custom labels (QTY, UNIT, INGREDIENT)
    # to the NER component
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2]) # ent[2] is the "LABEL"

    # 5. Start the training!
    # We'll disable other pipelines, so we only train the NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]

    with nlp.disable_pipes(*other_pipes):
        print("Starting training...")
        optimizer = nlp.begin_training()

        for itn in range(n_iter):
            # Shuffle the training data on each iteration
            random.shuffle(TRAIN_DATA)
            losses = {}

            # Batch up the examples
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))

            for batch in batches:
                examples = []
                for text, annots in batch:
                    try:
                        # Create an "Example" object for spaCy
                        doc = nlp.make_doc(text)
                        examples.append(Example.from_dict(doc, annots))
                    except ValueError as e:
                        # This catches bad labels (e.g., overlaps)
                        print(f"Warning: Skipping one bad example. Error: {e}")

                # 6. THIS IS THE CORE STEP:
                # Only update if we have valid examples in the batch
                if examples:
                    nlp.update(
                        examples,
                        drop=0.3, # Dropout - makes model more robust
                        sgd=optimizer,
                        losses=losses,
                    )

            print(f"Iteration {itn + 1}/{n_iter}, Losses: {losses}")

    # 7. Save our newly trained, custom model to a folder
    nlp.to_disk(model_dir)
    print(f"Training complete! Model saved to: {model_dir}")


# This just runs our main function when we call "python train_nlp.py"
if __name__ == "__main__":
    main()