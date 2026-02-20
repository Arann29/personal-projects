from functools import lru_cache

from transformers import pipeline


@lru_cache(maxsize=1)
def sentiment_pipeline():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def score_texts(texts: list[str]) -> list[dict]:
    classifier = sentiment_pipeline()
    raw = classifier(texts, truncation=True)
    results: list[dict] = []

    for row in raw:
        label = str(row["label"]).upper()
        results.append(
            {
                "sentiment_label": label,
                "sentiment_score": float(row["score"]),
            }
        )

    return results
