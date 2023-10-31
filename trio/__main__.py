"""Starts an interactive interpreter session that supports top-level
`await`-ing.

To start a new session, run the command:

.. code-block:: shell

   python -m trio

Modeled after the standard library's `asyncio.__main__`. See:

    https://github.com/python/cpython/blob/master/Lib/asyncio/__main__.py
"""
from __future__ import annotations

import ast
import code
import concurrent.futures
import inspect
import sys
import threading
import types
from collections.abc import Awaitable, Mapping
from typing import Any, TypeVar

import trio

T = TypeVar("T")


class TrioInteractiveConsole(code.InteractiveConsole):
    __slots__ = ("nursery",)

    def __init__(self, locals: Mapping[str, Any] | None, nursery: trio.Nursery) -> None:
        super().__init__(locals)
        self.compile.compiler.flags |= ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
        self.nursery = nursery

    def runcode(self, code: types.CodeType) -> None:
        func = types.FunctionType(code, dict(self.locals))
        future: concurrent.futures.Future[object] = concurrent.futures.Future()

        try:
            result = func()
        except SystemExit:
            raise
        except BaseException as exc:
            future.set_exception(exc)
        else:
            if not inspect.iscoroutine(result):
                future.set_result(result)
            else:
                await_in_bg = threading.Thread(
                    target=trio.run, args=(_await, result, future), daemon=True
                )
                await_in_bg.start()

        try:
            future.result()
            return
        except SystemExit:
            raise
        except KeyboardInterrupt:
            self.write("\nKeyboardInterrupt\n")
        except BaseException:
            self.showtraceback()


async def _await(awaitable: Awaitable[T], future: concurrent.futures.Future[T]) -> None:
    try:
        value = await awaitable
    except SystemExit:
        raise
    except BaseException as exc:
        future.set_exception(exc)
    else:
        future.set_result(value)


async def main(repl_locals: dict[str, object]) -> None:
    async with trio.open_nursery() as nursery:
        console = TrioInteractiveConsole(repl_locals, nursery)
        banner = (
            # types: attr-defined error: Module "trio" does not explicitly export attribute "__version__"
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_io_windows.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_local.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_mock_clock.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_multierror.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_parking_lot.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_run.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_unbounded_queue.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_wakeup_socketpair.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_dtls.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_highlevel_generic.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_highlevel_socket.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_path.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_socket.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_ssl.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_subprocess.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_subprocess_platform/waitid.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_sync.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_threads.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_unix_pipes.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_util.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/lowlevel.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/__init__.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/_check_streams.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/_checkpoints.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/_memory_streams.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/_sequencer.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/testing/_trio_test.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/__init__.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_channel.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_asyncgens.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_entry_queue.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_exceptions.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_generated_instrumentation.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_io_common.py
            # types: note: Another file has errors: /home/samuel/Desktop/Github Clones/trio-wbadart/trio/_core/_io_epoll.py
            f"Trio {trio.__version__}, "
            # types: ^^^^^^^^^^^^^^^
            f"Python {sys.version} on {sys.platform}\n"
            f'Use "await" directly instead of "trio.run()".\n'
            f'Type "help", "copyright", "credits" or "license" '
            f"for more information.\n"
            f'{getattr(sys, "ps1", ">>> ")}import trio'
        )
        console.interact(banner=banner, exitmsg="exiting Trio REPL...")


if __name__ == "__main__":
    repl_locals = {"trio": trio}
    for key in {
        "__name__",
        "__package__",
        "__loader__",
        "__spec__",
        "__builtins__",
        "__file__",
    }:
        repl_locals[key] = locals()[key]

    trio.run(main, repl_locals)
