import os
from joblib import dump, load
from nltk import word_tokenize, pos_tag
from nltk.chunk import conlltags2tree, tree2conlltags
from nltk.tag import UnigramTagger, BigramTagger
from nltk.chunk import ChunkParserI

from .BuildNERDataset import get_ner_dataset

def custom_tagger(original_text, tokens, entities):
    """
    Based on the stationNERDataset's entity mapping, tags each token with a entity label, and returns a list 
    >>> [('I', 'PRP', 'O'), ('wan', 'VBP', 'O'), ('na', 'RB', 'O'), ('go', 'VBP', 'O'), ('to', 'TO', 'O'), ('Brixton', 'NNP', 'B-DST'), ('from', 'IN', 'O'), ('Liverpool', 'NNP', 'B-DST'), ('Street', 'NNP', 'B-DST')]
    """
    DSTtokens, ORNtokens, result = [], [], []
    for entity in entities:
        item = original_text[entity[0]-1:entity[1]+1]
        if entity[2] == "DST":
            for DSTtoken in word_tokenize(item):
                DSTtokens.append(DSTtoken)
        if entity[2] == "ORN":
            for ORNtoken in word_tokenize(item):
                ORNtokens.append(ORNtoken)
    i = 0
    for token in tokens:    
        if token in DSTtokens: 
            result.append((token, "B-DST") if i == 0 else (token, "I-DST"))
            i += 1
        elif token in ORNtokens:
            result.append((token, "B-ORN") if i == 0 else (token, "I-ORN"))
            i += 1
        else:
            result.append((token, "O"))
            i = 0
    
    return result
        
# Convert dataset to the IOB format
def convert_to_iob(dataset):
    """
    Convert the dataset format to IOB tree.
    """
    iob_data = []
    for row in dataset:
        text, entities = row["text"], row["entities"]
        tokens = word_tokenize(text)
        labels = custom_tagger(text, tokens, entities)
        pos_tags = pos_tag(tokens)
        tree = conlltags2tree([(tokens[i], pos_tags[i][1], label) for i, (_, label) in enumerate(labels)])
        iob_data.append(tree)
    return iob_data

def conll_tag_chunks(chunk_sents):
	"""Convert each chunked sentence to list of (tag, chunk_tag) tuples,
	so the final result is a list of lists of (tag, chunk_tag) tuples.
	>>> from nltk.tree import Tree
	>>> t = Tree('S', [Tree('NP', [('the', 'DT'), ('book', 'NN')])])
	>>> conll_tag_chunks([t])
	[[('DT', 'B-NP'), ('NN', 'I-NP')]]
	"""
	tagged_sents = [tree2conlltags(tree) for tree in chunk_sents]
	return [[(pos_tag, chunk_tag) for (_, pos_tag, chunk_tag) in sent] for sent in tagged_sents]


class NamedEntityChunker(ChunkParserI):
    """
    Define a custom chunker using UnigramTagger
    """
    def __init__(self, train_sents):
        train_data = conll_tag_chunks(train_sents)
        self.tagger = BigramTagger(train_data)

    def parse(self, sentence):
        """Parsed tagged tokens into parse Tree of chunks"""
        if not sentence: return None
        (words, tags) = zip(*sentence)
        chunks = self.tagger.tag(tags)
        # create conll str for tree parsing
        conlltags = [(word, pos, chunktag) for (word, (pos, chunktag)) in zip(words, chunks)]
        return conlltags2tree(conlltags)

def buildModel():
    """ 
    Train the NLTK custom NER model and build a joblib file
    """
    if not os.path.exists("src/joblibs/nltk_ner_model_trainset.joblib"):
        dataset = get_ner_dataset()
        train_set = convert_to_iob(dataset)
        dump(train_set, "src/joblibs/nltk_ner_model_trainset.joblib")
    else:
        train_set = load("src/joblibs/nltk_ner_model_trainset.joblib")
    ner_chunker = NamedEntityChunker(train_set)
    print("Build completed!")
    return ner_chunker