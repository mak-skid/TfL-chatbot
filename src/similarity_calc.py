from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.stem.snowball import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter

def similarity_calc(key, intent_docs, query):
    """
    Stem, tokenise, filter, count, create tf-idf matrix and calculate cosine similarity,
    and returns a triple (key, index, cosine_similarity) if similarity is above 0.8. Otherwise, returns None.
    """
    p_stemmer = PorterStemmer()
    analyzer = CountVectorizer().build_analyzer()

    def stemmed_words(doc):
        return (p_stemmer.stem(w) for w in analyzer(doc))
    
    stemmed_count_vect = CountVectorizer(analyzer=stemmed_words)
    X_train_counts = stemmed_count_vect.fit_transform(intent_docs)
    X_query_counts = stemmed_count_vect.transform(query)
    tfidf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True)
    datasetTFIDF = tfidf_transformer.fit_transform(X_train_counts)
    queryTFIDF = tfidf_transformer.transform(X_query_counts)

    cosine_similarities = cosine_similarity(queryTFIDF, datasetTFIDF) 

    # Similarity threshold
    threshold = 0.6

    max_cosine_similarity = cosine_similarities.max()

    return key, cosine_similarities.flatten().argsort()[-1], max_cosine_similarity if max_cosine_similarity > threshold else None

def max_similarity(documents, query):
    """
    Returns the id of a row with max similarity by calculating max cosine similarity for each intent document
    """
    max_similarities = []

    for key, intent_docs in documents.items():
        max_similarity = similarity_calc(key, intent_docs.values(), query)
        if max_similarity[2]:
            max_similarities.append(max_similarity)

    if not max_similarities:
        return None
    
    max_similarity_index = max(max_similarities, key=itemgetter(2))
    return max_similarity_index[0] + str(max_similarity_index[1] + 1) if max_similarity_index else None 
    
