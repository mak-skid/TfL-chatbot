import spacy
from spacy import displacy

def findEntity(text):
    nlp_ner = spacy.load("model-last")  # location of your created model

    doc = nlp_ner(text)

    for ent in doc.ents:
        print(ent.text, ent.label_)

text = "I wanna take a tube from Langdon Park to Baker Street"
findEntity(text)
