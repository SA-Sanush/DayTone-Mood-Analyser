try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except Exception:  # pragma: no cover
    nltk = None
    SentimentIntensityAnalyzer = None


_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is not None:
        return _analyzer
    if SentimentIntensityAnalyzer is None:
        return None
    try:
        _analyzer = SentimentIntensityAnalyzer()
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def get_sentiment_score(text: str) -> float:
    if not text or not text.strip():
        return 0.0
    analyzer = _get_analyzer()
    if analyzer is None:
        return 0.0
    return float(analyzer.polarity_scores(text)["compound"])
