from collections import deque
from pathpy.util import SET_OF_STRS

from pathpy.adts.chain import Chain
from pathpy.adts.collection_wrapper import get_collection_wrapper

MAX_LOOKAHEAD = -1
WORD_MAX_LENGTH = -1
WORD_TYPE = get_collection_wrapper(list, list.append)
LANGUAGE_TYPE = SET_OF_STRS
ALTERNATIVES_COLLECTION_TYPE = get_collection_wrapper(
    deque, deque.appendleft, None, deque.popleft, IndexError)
ONLY_COMPLETE_WORDS = True
WORDS_COLLECTION_TYPE = get_collection_wrapper(
    Chain, extend=Chain.expand_right, pop=Chain.__next__, pop_exception=StopIteration)
