from question_extractor.extractor import *

model = load_model_()
sentences = "many ppl do this but. what is your name?"
results = extract_question(str(sentences), model)

if results:
    for sent in results:
        if is_question_post_filter(sent) == 1:
            print(f"{sent} is question...")
        else:
            print(f"{sent} is not a question...")