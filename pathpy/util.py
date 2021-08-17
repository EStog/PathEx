from pathpy.adts.collection_wrapper import get_collection_wrapper


def take(n, it):
    return (x for _, x in zip(range(n), it))


SET_OF_TUPLES = get_collection_wrapper(set, lambda s, w: s.add(tuple(w)))

SET_OF_STRS = get_collection_wrapper(
    set, lambda s, w: s.add(''.join(str(l) for l in w)))
