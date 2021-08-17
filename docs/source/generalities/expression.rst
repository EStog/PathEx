General explanation of expressions
==================================

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>

This section explains the concept of "expression" in general terms and in the context of |ppy|.

.. seealso::

   Document :doc:`/semantics/expression`
     A more rigorous explanation of the meaning of expressions.
   Class :class:`~.Expression`
     Abstract base class of expressions.

An expression is a combination of symbols that complies with a set of structural rules. An expression is uniquely associated with a composition of functions over a universe of formal languages. That is, an expression generates a formal language. A formal language is a set of words and a word is a finite sequence of letters [#disclamer]_.

For example, the expression :math:`(a|b) + c`, generates sequences which two elements. The first element is either :math:`a` or :math:`b` and the second is :math:`c`. In |ppy| idiom this may be expressed as:

>>> from pathpy.expressions.aliases import *
>>> expression = U('ab') + 'c'
>>> assert expression.get_language() == {'ac', 'bc'}

In this case a :mod:`short alias <pathpy.expressions.aliases>` of :class:`~.Union` and the overloaded operation :meth:`+ <pathpy.expressions.expression.Expression.__add__>` to express :class:`~.Concatenation` are being used to construct the desired expression. Method :meth:`~.get_language`, by default, gives the words represented as :class:`str` objects.

The previous example shows a case that generates a finite language. However, there are expressions which language is infinite or undetermined.

For example, the expression :math:`(a | b)*` generates a language which elements are the :doc:`empty word <empty_word>` or :math:`a` or :math:`b` several times repeated. In |ppy| idiom this may be expressed as:

>>> from pathpy.expressions.aliases import *
>>> from pathpy.utils import take
>>> from path
>>> expression = U('ab')*...
>>> assert {''.join() for w in take(5, words_generator(expression))}

.. todo:: Add reference to external documentation about formal languages

.. rubric:: Footnotes

.. [#disclamer] In other contexts, words are also called "strings". In these documents it is used the noun "word" to avoid confusion with :class:`str` which is meant to represent strings in a specific context and with a slightly --but importantly-- different semantic. Specifically in |ppy| a letter may be any instance of :class:`object`, so the set of all possible words is more diverse than the set of all possible strings (aka :class:`str` instances).
