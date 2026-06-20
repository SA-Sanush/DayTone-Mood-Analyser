"""Sentiment analysis module for DayTone journal notes.

Primary analyser: NLTK VADER (Valence Aware Dictionary and sEntiment Reasoner).

KNOWN LIMITATIONS OF VADER (academic transparency note):
  - VADER is a rule-based, lexicon-driven model. It is fast and requires no
    training data, but has the following structural limitations:
      1. Context blindness: "not great" and "great" are scored differently, but
         multi-word negations and complex sentence structure are often missed.
      2. No sarcasm detection: "Oh great, another awful day" may score falsely positive.
      3. Domain-specific distress language: clinical terms like "dissociation",
         "hopelessness", "anhedonia", or culturally specific expressions of
         emotional pain are absent from its lexicon.
      4. Short text penalty: very short entries (< 5 words) produce unreliable scores.

ENHANCEMENT PATH:
  If the `transformers` package (Hugging Face) is installed, the module will
  attempt to load a lightweight distilled BERT model
  (e.g. `distilbert-base-uncased-finetuned-sst-2-english`) for improved
  contextual accuracy. This is optional and falls back silently to VADER.
  Enabling this in production requires ~250MB disk space and ≥1s inference
  overhead per entry on CPU — acceptable for a mini-project, but document
  this tradeoff in the viva.
"""

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except (ImportError, LookupError, OSError):  # pragma: no cover
    nltk = None
    SentimentIntensityAnalyzer = None

# Optional: lightweight BERT-based sentiment (graceful fallback to VADER)
try:
    from transformers import pipeline as hf_pipeline
    _HF_AVAILABLE = True
except ImportError:  # pragma: no cover
    _HF_AVAILABLE = False


_analyzer = None
_hf_model = None
_USE_HF = False  # Set to True only when transformers pipeline loads successfully


def _try_load_hf_pipeline():
    """Attempt to load a lightweight HuggingFace distilled BERT sentiment pipeline.

    This is tried once at startup. If it fails (e.g., no internet, missing
    weights, or transformers not installed), the system silently falls back
    to VADER. The active backend is logged once during initialization.
    """
    global _hf_model, _USE_HF
    if not _HF_AVAILABLE:
        return
    try:
        _hf_model = hf_pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True,
            max_length=512,
        )
        _USE_HF = True
    except Exception:  # pragma: no cover
        _hf_model = None
        _USE_HF = False


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


def _hf_score_to_compound(result: dict) -> float:
    """Convert HuggingFace pipeline output (label + score) to a [-1, 1] compound.

    HF returns: {"label": "POSITIVE"/"NEGATIVE", "score": 0.0–1.0}
    We map POSITIVE → +score, NEGATIVE → -score, matching VADER's convention.
    """
    label = result.get("label", "").upper()
    score = float(result.get("score", 0.5))
    if label == "POSITIVE":
        return round(score, 4)
    elif label == "NEGATIVE":
        return round(-score, 4)
    return 0.0


def get_sentiment_score(text: str) -> float:
    """Analyse a journal entry and return a compound sentiment score in [-1, 1].

    Positive values indicate positive sentiment; negative values indicate
    negative sentiment; values near 0 are neutral.

    Backend priority:
      1. HuggingFace distilled BERT (if `transformers` is installed and loaded)
      2. NLTK VADER (default for all installations)
      3. Returns 0.0 if neither is available (safe degraded mode)
    """
    if not text or not text.strip():
        return 0.0

    # Try HuggingFace contextual model first
    if _USE_HF and _hf_model is not None:
        try:
            result = _hf_model(text[:512])[0]
            return _hf_score_to_compound(result)
        except Exception:  # pragma: no cover
            pass  # Fall through to VADER

    # Fall back to VADER
    analyzer = _get_analyzer()
    if analyzer is None:
        return 0.0
    return float(analyzer.polarity_scores(text)["compound"])


def get_sentiment_backend() -> str:
    """Return the name of the active sentiment backend for admin diagnostics."""
    if _USE_HF:
        return "DistilBERT (HuggingFace)"
    if _get_analyzer() is not None:
        return "VADER (NLTK)"
    return "Unavailable"
