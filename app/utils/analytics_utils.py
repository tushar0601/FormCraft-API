from keybert import KeyBERT
from typing import List
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from pydantic import BaseModel

nltk.download("vader_lexicon")
nltk.download("punkt")
nltk.download("punkt_tab")

kw_model = KeyBERT()
sia = SentimentIntensityAnalyzer()


class SentimentResponse(BaseModel):
    positive: int
    neutral: int
    negative: int


class AnalyzeResponse(BaseModel):
    length: int
    top_keywords: List[str]
    sentiment_counts: SentimentResponse


def analyze_text(text: str, top_n: int = 10) -> AnalyzeResponse:
    cleaned = (text or "").strip()
    if not cleaned:
        return AnalyzeResponse(
            length=0,
            top_keywords=[],
            sentiment_counts=SentimentResponse(positive=0, neutral=0, negative=0),
        )

    try:
        raw_kw = kw_model.extract_keywords(
            cleaned, top_n=max(1, min(top_n, 50)), use_mmr=True, diversity=0.5
        )
        kws = []
        seen = set()
        for k, _score in raw_kw:
            k2 = (k or "").strip().lower()
            if not k2 or k2 in seen:
                continue
            seen.add(k2)
            kws.append(k2)
    except Exception:
        kws = []

    sentences = nltk.sent_tokenize(cleaned) or [cleaned]
    pos = neg = neu = 0
    for s in sentences:
        compound = sia.polarity_scores(s)["compound"]
        if compound > 0.05:
            pos += 1
        elif compound < -0.05:
            neg += 1
        else:
            neu += 1

    return AnalyzeResponse(
        length=len(nltk.word_tokenize(cleaned)),
        top_keywords=kws,
        sentiment_counts=SentimentResponse(positive=pos, neutral=neu, negative=neg),
    )
