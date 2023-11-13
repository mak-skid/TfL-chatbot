from joblib import dump, load
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.stem.snowball import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity


def similarity_calc(documents, query):
    """
    Stem, tokenise, filter, count, create tf-idf matrix and calculate cosine similarity
    In order to perform stemming and stopwords removal, 
    implemented StemmedCountVectorizer which overrides CountVectorizer 
    so that we have our own custom build_analyzer
    Snippet from https://stackoverflow.com/questions/36182502
    
    class StemmedCountVectorizer(CountVectorizer):
        def build_analyzer(self):
            analyzer = super(StemmedCountVectorizer, self).build_analyzer()
            return lambda doc: ([p_stemmer.stem(w) for w in analyzer(doc)])
    """
    p_stemmer = PorterStemmer()
    analyzer = CountVectorizer().build_analyzer()

    def stemmed_words(doc):
        return (p_stemmer.stem(w) for w in analyzer(doc))
    
    stemmed_count_vect = CountVectorizer(analyzer=stemmed_words)
    X_train_counts = stemmed_count_vect.fit_transform(documents)
    X_query_counts = stemmed_count_vect.transform(query)
    tfidf_transformer = TfidfTransformer(use_idf=True, sublinear_tf=True)
    datasetTFIDF = tfidf_transformer.fit_transform(X_train_counts)
    queryTFIDF = tfidf_transformer.transform(X_query_counts)

    cosine_similarities = cosine_similarity(queryTFIDF, datasetTFIDF).flatten()

    return cosine_similarities.argsort()[:-2:-1]
    
    
