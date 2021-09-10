.. PathEx documentation master file, created by
   sphinx-quickstart on Sat Aug 14 23:11:47 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to |pe|'s documentation!
================================

The main goal of |pe| library is to ease concurrent programming in Python by separating the specification of synchronization from the main logic aspect. Path expressions [#pe_ref]_ is the selected theoretical framework to achieve this goal. In this model, the allowed execution paths are specified declaratively by using constructions similar to regular expressions.

.. caution:: **Library in development**

   This library is currently **in development**, and it is not recommended being used in production environments.

.. warning:: **Documentation in development**

   These documents are currently **in development**, and in an incomplete state.

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   overview
   generalities/index
   semantics/index
   references
   API/pathex

.. todo:: add *license*

.. todo:: add *introduction*

.. todo:: add *how to collaborate*

.. todo:: add *how to read this docs*

.. todo:: add *glossary*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. ifconfig:: todo_include_todos == True

   To be done
   ==========

   .. todolist::

.. rubric:: Footnotes

.. [#pe_ref] Paths expressions were proposed by :cite:t:`campbell_specification_1974`. Important extensions and variants may be found in :cite:t:`habermann_path_1975,campbell_path_1976,andler_predicate_1979,headington_open_1984,govindarajan_parc_1991,guo_synchronization_1994,heinlein_advanced_2003,zhao_sc-expressions_2007`.
