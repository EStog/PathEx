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

.. highlight:: python

Usage
-----

First, construct some tags that will represent the regions to be synchronized:

.. testcode:: threads_decorator,threads_contextmanager,processes_decorator,processes_contextmanager

   from pathex import Tag

   writer, reader = Tag.named('writer', 'reader')

Then, create an expression that specify the allowed paths of execution:

.. testcode:: threads_decorator,threads_contextmanager,processes_decorator,processes_contextmanager

   exp = (writer | reader//...)+...

In this case the expression specify that a single writer or a set of concurrent readers may be executed. Also, these paths of execution may be repeated many times in sequence. For example, the following is an allowed path [#]_: ``reader writer writer {reader, reader} writer``, but the following is not: ``{reader writer} writer {reader, reader} writer``.

.. [#] ``{`` and ``}`` are used to specify a set of concurrent tasks.

Next, if you are using threads, create a :class:`~.Synchronizer` that will serve as a manager of the execution flow.

.. testcode:: threads_decorator,threads_contextmanager

   from pathex import Synchronizer

   sync = Synchronizer(exp)

In the case of processes, use :func:`~.get_synchronizer` instead:

.. testcode:: processes_decorator,processes_contextmanager

   from pathex import Tag, get_synchronizer

   sync = get_synchronizer(exp)

To mark a function as a region to be synchronized use :meth:`~pathex.managing.manager.Manager.region`. It can be used in the case of threads as well as in the case of processes. For example:

.. testcode:: threads_decorator,processes_decorator

   @sync.region(writer)
   def append(shared_buffer, x):
       shared_buffer.append(x)

   @sync.region(reader)
   def get_top(shared_buffer):
       try:
          x = shared_buffer[0]
       except Exception:
          return None
       else:
          return x

   @sync.region(writer)
   def appendleft(shared_buffer, x):
       shared_buffer.insert(0, x)

:meth:`~pathex.managing.manager.Manager.region` can be used as a context manager as well:

.. testcode:: threads_contextmanager,processes_contextmanager

   def append(shared_buffer, x):
       with sync.region(writer):
          shared_buffer.append(x)

   def get_top(shared_buffer):
       with sync.region(reader):
          try:
             x = shared_buffer[0]
          except Exception:
             return None
          else:
             return x

   def appendleft(shared_buffer, x):
       with sync.region(writer):
          shared_buffer.insert(0, x)

In the shown examples ``shared_buffer`` may be specified as a global variable, but it is a good practice to define it as a parameter to use a common idiom no matter we are using threads or processes.

Once the regions to be synchronized are specified, threads (or processes) may be started by using any of the known standard methods. For example, we may define a function to spawn the concurrent tasks, that takes an :class:`~concurrent.futures.Executor` class and a shared buffer:

.. testcode:: threads_decorator,threads_contextmanager,processes_decorator,processes_contextmanager

   def spawn_tasks(Executor, shared_buffer):
       tasks = []

       with Executor() as executor:
          tasks.extend([executor.submit(append, shared_buffer, 4) for _ in range(5)])
          tasks.extend([executor.submit(get_top, shared_buffer) for _ in range(5)])
          tasks.extend([executor.submit(appendleft, shared_buffer, 3) for _ in range(5)])

          done, not_done = cf.wait(tasks, timeout=None, return_when=cf.ALL_COMPLETED)
          assert not not_done

In the case of threads we use :class:`~concurrent.futures.ThreadPoolExecutor` and a simple :class:`~list` as a shared buffer:

.. testcode:: threads_decorator,threads_contextmanager

   if __name__ == '__main__':

      from concurrent.futures import ThreadPoolExecutor

      shared_buffer = []

      spawn_tasks(ThreadPoolExecutor, shared_buffer)

      assert shared_buffer == [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]

The condition ``if __name__ == '__main__': ...`` is not necessary for threads, but it is a good practice to use it as a common idiom for threads and processes.

In the case of processes :class:`~concurrent.futures.ProcessPoolExecutor` may be used and a :ref:`proxy <multiprocessing-proxy_objects>` to a :class:`~list` obtained from the underlain :class:`~multiprocessing.managers.SyncManager` as the shared proxy.

.. testcode:: processes_decorator,processes_contextmanager

   if __name__ == '__main__':

      from concurrent.futures import ProcessPoolExecutor

      manager = sync.get_mp_manager()
      shared = manager.list()

      spawn_tasks(ProcessPoolExecutor, shared_buffer)

      assert list(shared_buffer) == [3, 3, 3, 3, 3, 4, 4, 4, 4, 4]

In any case, the synchronizer will manage any request of execution and will allow only those in accord with the given expression and the current state of execution. Disallowed requests are suspended until the appropriate execution conditions are met.
