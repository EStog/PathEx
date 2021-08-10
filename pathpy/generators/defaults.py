from collections import deque

from pathpy.adts.chain import Chain
from pathpy.adts.collection_wrapper import get_collection_wrapper

MAX_LOOKAHEAD = 100
WORD_TYPE = get_collection_wrapper(list, list.append)
LANGUAGE_TYPE = get_collection_wrapper(
    set, lambda s, w: s.add(''.join(str(l) for l in w)))
ALTERNATIVES_COLLECTION_TYPE = get_collection_wrapper(
    deque, deque.appendleft, None, deque.popleft, IndexError)
ONLY_COMPLETE_WORDS = True
WORDS_COLLECTION_TYPE = get_collection_wrapper(
    Chain, extend=Chain.expand_right, pop=Chain.__next__, pop_exception=StopIteration)
