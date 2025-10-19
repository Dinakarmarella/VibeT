from sklearn.feature_extraction.text import TfidfVectorizer

def get_vectorizer(max_features=3000, ngram_range=(1,2)):
    return TfidfVectorizer(
        ngram_range=ngram_range,
        min_df=2,
        max_features=max_features
    )
