import doctest


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.cached_generators.cached_generator'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.cached_generators.cached_generator_method'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.chain'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.containers.head_tail_iterable'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.containers.queue_set'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.collection_wrapper'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.multitask.acquired_lock'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.multitask.atomics.atomic'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.multitask.atomics.atomic_attribute'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.multitask.atomics.atomic_integer'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.multitask.shared_lock'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.adts.singleton'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.expression'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.concatenation'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.difference'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.intersection'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.shuffle'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.synchronization'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.nary_operators.union'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.repetitions.concatenation_repetition'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.expressions.repetitions.shuffle_repetition'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.managing.synchronizer'))
    tests.addTests(doctest.DocTestSuite(
        'pathpy.managing.trace_checker'))
    return tests
