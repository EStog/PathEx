Generalities of expressions
===========================

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

------------------------

This section explains the concept of "expression" in general terms and in the context of |ppy|.

.. seealso::

   Document :doc:`/semantics/expressions/index`
     A more rigorous explanation of the meaning of expressions.
   Class :class:`~.Expression`
     Abstract base class of expressions.

An expression is a combination of symbols that complies with a set of structural rules. An expression is uniquely associated with a composition of functions over a universe of formal languages. That is, an expression generates a formal language. A formal language is a set of words and a word is a finite sequence of letters [#disclamer]_.

.. todo:: Describe which are the available expression operators.

For example, the expression :math:`(a|b)c`, generates sequences which two elements. The first element is either :math:`a` or :math:`b` and the second is :math:`c`. In |ppy| idiom this may be expressed as:

>>> from pathex.expressions.aliases import *
>>> expression = U('ab') + 'c'
>>> assert expression.get_language() == {'ac', 'bc'}

In this case ``U`` is a :mod:`short alias <pathex.expressions.aliases>` of :class:`~.Union` and the overloaded operation :meth:`+ <pathex.expressions.expression.Expression.__add__>` that express :class:`~.Concatenation` is being used to construct the desired expression. Method :meth:`get_language <pathex.expressions.expression.Expression.get_language>`, by default, gives the words as :class:`str` objects.

The previous example shows a case that generates a finite language. However, there are expressions which language is infinite. For example, the expression :math:`(ab)*` generates a language which elements are the :doc:`empty word <empty_word>` or :math:`ab` several times repeated. In |ppy| idiom this may be expressed as:

.. >>> from pathex.expressions.aliases import *
>>> from pathex.adts.util import take
>>> expression = C('ab')*...
>>> assert {''.join(str(l) for l in w) for w in take(5, expression.get_eager_generator())} == \
...   {'', 'ab', 'abab', 'ababab', 'abababab'}
>>> assert {''.join(str(l) for l in w) for w in take(7, expression.get_eager_generator())} == \
...   {'', 'ab', 'abab', 'ababab', 'abababab', 'ababababab', 'abababababab'}

In this case ``C`` is a :mod:`short alias <pathex.expressions.aliases>` of :class:`~.Concatenation`, and the overloaded operator :meth:`* <pathex.expressions.expression.Expression.__mul__>` with operand :data:`... <Ellipsis>` is used to construct an unbounded repetition. Because the generated language is infinite, helper function :func:`~.take` has being used to select specific amounts of words. The words are taken from the generator returned by :meth:`~.get_eager_generator`.

Other expressions generate undetermined languages. This occurs in the presence of one or various :doc:`negations <negation>` that can not be simplified to a concrete set of values. For example, the expression :math:`-(a|b)*` generates a language which words do not contain :math:`a` nor :math:`b` as elements. In this case, although it is clear what any word of the language can not have, it is not clear what it may have, so possible constituent words can not be given specifically. In |ppy| idiom this may be expressed as:



------------------------

There are various kinds of expressions, which general documentation may be found in the following list:

.. toctree::
    :maxdepth: 2

    Empty word <empty_word>
    Union <union>

.. todo:: Add reference to external documentation about formal languages

.. rubric:: Footnotes

.. [#disclamer] In other contexts, words are also called "strings". In these documents it is used the noun "word" to avoid confusion with :class:`str` which is meant to represent strings in a specific context and with a slightly --but importantly-- different semantic. Specifically in |ppy| a letter may be any instance of :class:`object`, so the set of all possible words is more diverse than the set of all possible strings (aka :class:`str` instances).
