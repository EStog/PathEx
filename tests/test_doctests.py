import doctest


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.cached_generators.cached_generator'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.cached_generators.cached_generator_method'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.chain'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.containers.head_tail_iterable'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.containers.ordered_set'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.collection_wrapper'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.multitask.counted_condition'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.multitask.atomics.atomic'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.multitask.atomics.atomic_attribute'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.multitask.atomics.atomic_integer'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.multitask.shared_lock'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.singleton'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.adts.util'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.expression'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.concatenation'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.difference'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.intersection'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.shuffle'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.synchronization'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.nary_operators.union'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.repetitions.concatenation_repetition'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.repetitions.shuffle_repetition'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.terms.letters_complement'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.expressions.terms.alphabet'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.managing.synchronizer'))
    tests.addTests(doctest.DocTestSuite(
        'pathex.managing.trace_checker'))
    return tests
