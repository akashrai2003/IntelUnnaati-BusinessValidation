import nltk



def find_clauses(text):
    """
    Find clauses in text.

    Args:
        text (str): The text to find clauses in.
        
    Returns:
        List: A list of clauses found in the text.
    """
    # Split the text into sentences
    sentences = nltk.sent_tokenize(text)
    clauses = []
    for sentence in sentences:
        # Split the sentence into clauses
        clause_list = nltk.chunk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sentence)))
        for clause in clause_list:
            if isinstance(clause, nltk.Tree):
                clauses.append(" ".join([token for token, tag in clause.leaves()]))
    return clauses