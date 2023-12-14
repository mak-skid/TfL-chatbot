from __future__ import unicode_literals, print_function
from BuildNERDataset import get_ner_dataset
from pathlib import Path
import spacy
from tqdm import tqdm
from spacy.tokens import DocBin
from spacy.util import filter_spans

model = None
output_dir=Path("./Models")
n_iter=100

if model is not None:
    nlp = spacy.load(model)  
    print("Loaded model '%s'" % model)
else:
    nlp = spacy.blank('en')
    doc_bin = DocBin()  
    print("Created blank 'en' model")

train_data = get_ner_dataset()

for training_example in tqdm(train_data): 
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

doc_bin.to_disk("./training_data.spacy") # save the docbin object    



