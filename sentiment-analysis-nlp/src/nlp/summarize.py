from collections import Counter

from openai import OpenAI

from src.config import settings


def _fallback_summary(sentiments: list[str], topic_keywords: list[str]) -> str:
    sentiment_counts = Counter(sentiments)
    topic_counts = Counter(topic_keywords)

    top_topics = [item[0] for item in topic_counts.most_common(3)]
    return (
        f"Sentiment distribution: {dict(sentiment_counts)}. "
        f"Most frequent topic clusters: {top_topics}. "
        "Use these clusters to decide where customer feedback is strongest and where action is needed."
    )


def generate_summary(sentiments: list[str], topic_keywords: list[str], sample_texts: list[str]) -> str:
    if not settings.openai_api_key:
        return _fallback_summary(sentiments, topic_keywords)

    try:
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "Summarize sentiment and topic analysis in 4 short bullet points. "
            "Use plain business language. Mention limits if confidence is mixed."
        )

        completion = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You summarize analytics clearly and conservatively."},
                {
                    "role": "user",
                    "content": (
                        f"{prompt}\n\n"
                        f"Sentiments: {sentiments}\n"
                        f"Topic keywords: {topic_keywords}\n"
                        f"Sample texts: {sample_texts[:10]}"
                    ),
                },
            ],
        )
        return completion.choices[0].message.content or _fallback_summary(sentiments, topic_keywords)
    except Exception:
        return _fallback_summary(sentiments, topic_keywords)
