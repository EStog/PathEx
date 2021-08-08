from collections import deque

from pathpy.adts.collection_wrapper import get_collection_wrapper

WORD_TYPE = get_collection_wrapper(list, list.append)
LANGUAGE_TYPE = get_collection_wrapper(
    set, lambda s, w: s.add(''.join(str(l) for l in w)))
ALTERNATIVES_COLLECTION_TYPE = get_collection_wrapper(
    deque, deque.appendleft, deque.extendleft, deque.popleft, IndexError)
ONLY_COMPLETE_WORDS = True
