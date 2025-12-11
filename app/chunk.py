def sliding_window_chunk(text: str, window_size: int=200, overlap: int=50):
    """
    Creates a sliding-window chunks from the text 
    """

    tokens = text.split() # split the text string into sub-strings while separating spaces 
    chunks = []           # empty list that will contains all the final chunks
    start = 0             # starting index of the chunk

    while start < len(tokens):
        end = start + window_size  # ending index of the chunk
        chunk_tokens = tokens[start:end]  # get the chunk tokens
        chunk_text = ' '.join(chunk_tokens)     # join the tokens to form a chunk string
        """
        tokens[start:end] → all tokens between start inclusive and end exclusive.
        If end exceeds the length of tokens, Python does not crash:
        tokens[150:999999] → just the tokens from 150 to the end.
        So even if end > len(tokens), it gives a shorter chunk, which is OK.
        """
        chunks.append(chunk_text)  # add the chunk string to the list of chunks

        start += window_size - overlap  # move the start index forward by window_size - overlap
        """
        Start sequence:
            start = 0 → chunk 1: tokens[0:200]
            start = 0 + 150 = 150 → chunk 2: tokens[150:350]
            start = 150 + 150 = 300 → chunk 3: tokens[300:500]
            etc.
        """
        if end >= len(tokens):
            break
    
    return chunks
