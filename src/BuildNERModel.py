from __future__ import unicode_literals, print_function
from BuildNERDataset import get_ner_dataset
import plac
import random
from pathlib import Path
import spacy
from spacy.training.example import Example
from tqdm import tqdm
from spacy.tokens import DocBin
from spacy.util import filter_spans

model = None
output_dir=Path("./NERModel")
n_iter=100

if model is not None:
    nlp = spacy.load(model)  
    print("Loaded model '%s'" % model)
else:
    nlp = spacy.blank('en')
    doc_bin = DocBin()  
    print("Created blank 'en' model")

TRAIN_DATA = get_ner_dataset()

#set up the pipeline
"""
if 'ner' not in nlp.pipe_names:
    nlp.add_pipe('ner', last=True)

ner = nlp.get_pipe('ner')

for row in TRAIN_DATA:
    print()
    annotations = row["entities"]
    for ent in annotations:
        ner.add_label(ent[2])

other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
with nlp.disable_pipes(*other_pipes):  # only train NER
    optimizer = nlp.begin_training()
    
    for itn in range(n_iter):
    random.shuffle(TRAIN_DATA)
    
    for text, annotations in tqdm(TRAIN_DATA):
        nlp.update(
            [text],  
            [annotations],  
            drop=0.5,  
            sgd=optimizer,
            losses=losses)
    
    losses = {}
    examples = []
    for row in TRAIN_DATA:
        example = Example.from_dict(nlp.make_doc(row["text"]), row["entities"])
        examples.append(example)
    
    nlp.update(examples, drop=0.5, sgd=optimizer, losses=losses)

    print(losses)

for row in TRAIN_DATA:
    doc = nlp(row["text"])
    print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
"""

for training_example in tqdm(TRAIN_DATA): 
    text = training_example['text']
    labels = training_example['entities']
    doc = nlp.make_doc(text) 
    ents = []
    for start, end, label in labels:
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    filtered_ents = filter_spans(ents)
    doc.ents = filtered_ents 
    doc_bin.add(doc)

doc_bin.to_disk("training_data.spacy") # save the docbin object    



