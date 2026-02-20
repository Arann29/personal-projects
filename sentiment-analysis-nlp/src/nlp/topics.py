import math

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def build_topics(texts: list[str], requested_topics: int) -> tuple[list[int], dict[int, str], int]:
    if not texts:
        raise ValueError("No texts available for topic modeling")

    max_topics = max(2, min(requested_topics, len(texts)))
    vectorizer = TfidfVectorizer(max_features=1200, ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    if matrix.shape[0] < 2:
        return [0], {0: "single-document"}, 1

    topic_count = min(max_topics, matrix.shape[0])
    topic_count = max(2, int(math.sqrt(matrix.shape[0]))) if topic_count > matrix.shape[0] else topic_count
    topic_count = min(topic_count, matrix.shape[0])

    model = KMeans(n_clusters=topic_count, random_state=42, n_init="auto")
    assignments = model.fit_predict(matrix)

    feature_names = vectorizer.get_feature_names_out()
    keywords_by_topic: dict[int, str] = {}

    for topic_id in range(topic_count):
        centroid = model.cluster_centers_[topic_id]
        top_idx = centroid.argsort()[-5:][::-1]
        keywords = [feature_names[index] for index in top_idx]
        keywords_by_topic[topic_id] = ", ".join(keywords)

    return assignments.tolist(), keywords_by_topic, topic_count
