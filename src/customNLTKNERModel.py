import os
from joblib import load
from Models.BuildNERDataset import get_ner_dataset
from Models.BuildNLTKNERModel import buildModel, convert_to_iob
from nltk import word_tokenize, pos_tag, tree2conlltags

class NLTKModel():
    def __init__(self):
        self.ner_chunker = buildModel()
        self.ents = []

    def evaluate(self):
        # Evaluate the custom NER model
        dataset = get_ner_dataset() 
        iob_data = convert_to_iob(dataset)
        accuracy = self.ner_chunker.accuracy(iob_data)
        print(f"Accuracy: {accuracy}")
    
    def getDoc(self, text):
        test_sentence = word_tokenize(text)
        ner_result = self.ner_chunker.parse(pos_tag(test_sentence))
        print(ner_result)
        conll_result = tree2conlltags(ner_result)

        class entity():
            def __init__(self):
                self.text = ""
                self.label_ = ""

        dst, orn = [], []
        for token in conll_result:
            if "DST" in token[2]:
                dst.append(token[0])
            elif "ORN" in token[2]:
                orn.append(token[0])
            else:
                ent = entity()
                if dst:
                    text = " ".join(dst)
                    dst = []
                    ent.text, ent.label_ = text, "DST"
                    self.ents.append(ent)
                if orn:
                    text = " ".join(orn)
                    orn = []
                    ent.text, ent.label_ = text, "ORN"
                    self.ents.append(ent)
        ent = entity()
        if dst:
            text = " ".join(dst)
            dst = []
            ent.text, ent.label_ = text, "DST"
            self.ents.append(ent)
        if orn:
            text = " ".join(orn)
            orn = []
            ent.text, ent.label_ = text, "ORN"
            self.ents.append(ent)        
            
        return self