import tiktoken
from typing import List, Optional

convert_history_to_text = lambda lst: ' '.join(f"{key}: {value}" for conversation in lst for key, value in conversation.items())
#convert_history_to_text =lambda idx_lst: ' '.join(idx_lst)
combine_index = lambda idx_lst: ' '.join(idx_lst)
RATIO_OF_INDEX_TO_HISTORY = 5

def trim_history_and_index_combined(history: List, index: List, max_token_length: int, model_name: Optional[str] = "gpt-4") -> List[dict]:
    # start trimming from index first
    trimming_idx = 1
    encoding = tiktoken.encoding_for_model(model_name)
    current_token_length = len(encoding.encode(convert_history_to_text(history) + combine_index(index)))

    while current_token_length > max_token_length:
        # Index is ranking based on relevance, remove the last element (least relevant)
        if len(index) and trimming_idx % (RATIO_OF_INDEX_TO_HISTORY + 1) != 0:
            index.pop()
        # Remove the oldest conversation, first element containing user query and second element containing assistant response
        elif len(history):
            history = history[2:]
        current_token_length = len(encoding.encode(convert_history_to_text(history) + combine_index(index)))

        trimming_idx += 1
    
    return history, index
