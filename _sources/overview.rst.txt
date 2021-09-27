Overview
========

.. sectionauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>
.. codeauthor:: Ernesto Soto Gómez <esto.yinyang@gmail.com>


This section roughly presents the main features of |pe|.

.. seealso::

   Document :doc:`/generalities/index`
     A more in depth explanation of |pe| features.
   Document :doc:`/semantics/index`
     A more rigorous explanation of |pe| features.

Usage
-----

First, construct some tags that will represent the regions to be synchronized:

.. testcode:: threads_register,threads_region,process_register,process_region

   from pathex import Tag

   writer, reader = Tag.named('writer', 'reader')

Then, create an expression that specify the allowed paths of execution:

.. testcode:: threads_register,threads_region,process_register,process_region

   exp = (writer | reader//...)+...

In this case the expression specify that a single writer or a set of concurrent readers may be executed. Also, these paths of execution may be repeated many times in sequence. For example, the following is an allowed path [#]_: ``reader writer writer {reader, reader} writer``, but the following is not: ``{reader writer} writer {reader, reader} writer``.

.. [#] ``{`` and ``}`` are used to specify a set of concurrent tasks.

Using threads
^^^^^^^^^^^^^

Next, create a :class:`~.Synchronizer` that will serve as a manager of the execution flow. Threads as execution units will be explained in this section. The case of processes will be explained in :ref:`another <using-processes>`.

In the case of threads as execution units, create a direct instance of :class:`~.Synchronizer`.

.. testcode:: threads_register,threads_region

   from pathex import Synchronizer

   sync = Synchronizer(exp)

There are two recommended ways of marking portions of code as tasks code to be synchronized. The first is by decorating functions with :meth:`~pathex.managing.manager.Manager.register`. For example:

.. testcode:: threads_register

   from collections import deque

   shared_buffer = deque()

   @sync.register(writer)
   def append(x):
       shared_buffer.append(x)

   @sync.register(reader)
   def get_top():
       try:
          x = shared_buffer[0]
       except Exception:
          return None
       else:
          return x

   @sync.register(writer)
   def appendleft(x):
       shared_buffer.appendleft(x)

The other way is by using context manager style with :meth:`~pathex.managing.manager.Manager.region`:

.. testcode:: threads_region

   from collections import deque

   shared_buffer = deque()

   def append(x):
       with sync.region(writer):
          shared_buffer.append(x)

   def get_top():
       with sync.region(reader):
          try:
             x = shared_buffer[0]
          except Exception:
             return None
          else:
             return x

   def appendleft(x):
       with sync.region(writer):
          shared_buffer.appendleft(x)

Once the regions to be synchronized are specified, threads may be started by using any of the known standard methods. For example, by using :class:`concurrent.futures.ThreadPoolExecutor`:

.. testcode:: threads_register,threads_region

   from concurrent.futures import ThreadPoolExecutor

   with ThreadPoolExecutor() as executor:
       _ = [executor.submit(append, 4) for _ in range(5)]
       _ = [executor.submit(get_top) for _ in range(5)]
       _ = [executor.submit(appendleft, 3) for _ in range(5)]

   assert shared_buffer == deque([3, 3, 3, 3, 3, 4, 4, 4, 4, 4])

The synchronizer will manage any request of execution and will allow only those in accord with the given expression and the current state of execution. The not allowed requests are suspended until the proper execution conditions are met.

.. _using-processes:

Using processes
^^^^^^^^^^^^^^^

If processes are to be used as execution units, the same general steps are to be followed but with some differences.

To decorate functions use :func:`~.process_register` instead of :meth:`~pathex.managing.manager.Manager.register`:

.. testcode:: process_register

   from pathex import process_register

   @process_register(writer)
   def append(shared_buffer, x):
       shared_buffer.append(x)

   @process_register(reader)
   def get_top(shared_buffer):
       try:
          x = shared_buffer[0]
       except Exception:
          return None
       else:
          return x

   @process_register(writer)
   def appendleft(shared_buffer, x):
       shared_buffer.insert(0, x)

To use context manager style use :func:`~.process_region` instead of :meth:`~pathex.managing.manager.Manager.region`:

.. testcode:: process_region

   from pathex import process_region

   def append(shared_buffer, x):
       with process_region(writer):
           shared_buffer.append(x)

   def get_top(shared_buffer):
       with process_region(reader):
          try:
             x = shared_buffer[0]
          except Exception:
             return None
          else:
             return x

   def appendleft(shared_buffer, x):
       with process_region(writer):
          shared_buffer.insert(0, x)

Then, in the ``__main__`` module get a :class:`~pathex.managing.process_synchronizer.SynchronizerProxy` by using :func:`~.process_synchronizer` and start processes by using any of the ways provided by |pe|. For example, with :class:`~pathex.managing.process_synchronizer.ProcessPoolExecutor`:

.. testcode:: process_register,process_region

   if __name__ == '__main__':

      from multiprocessing.managers import SyncManager

      from pathex import process_synchronizer, ProcessPoolExecutor

      psync = process_manager(
          exp, manager_class=SyncManager)

      shared_buffer = psync.list()

      with ProcessPoolExecutor(psync.address, max_workers=4) as executor:
          _ = [executor.submit(append, shared_buffer, 4) for _ in range(5)]
          _ = [executor.submit(get_top, shared_buffer) for _ in range(5)]
          _ = [executor.submit(appendleft, shared_buffer, 3) for _ in range(5)]

      assert list(shared_buffer) == [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]
