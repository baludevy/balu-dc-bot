def match_space_fuzzy(text: str, query: str, splitter: str = " ") -> bool:
    """
    Match all query fragments against text words. Words don't need to be in order,
    and fragments can partially match words.
    """
    text_words = text.lower().split(splitter)
    query_fragments = query.lower().split(splitter)
    for fragment in query_fragments:
        if not any(fragment in word for word in text_words):
            return False
    return True