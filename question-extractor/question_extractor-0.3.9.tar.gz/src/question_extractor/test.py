from question_extractor.question_extractor import *


model = load_model_()
sentence = "many ppl do this but. what is your name?"
sentence = extract_question(str(sentence), model)

print(sentence)
