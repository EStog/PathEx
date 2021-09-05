from collections import deque
from pathex.adts.util import SET_OF_STRS

from pathex.adts.collection_wrapper import get_collection_wrapper

MAX_LOOKAHEAD = -1
WORD_MAX_LENGTH = -1
WORD_TYPE = get_collection_wrapper(list, list.append)
LANGUAGE_TYPE = SET_OF_STRS
COLLECTION_TYPE = get_collection_wrapper(
    deque, deque.append, None, deque.popleft, IndexError)
COMPLETE_WORDS = True
