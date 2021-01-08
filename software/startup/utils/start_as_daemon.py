from multiprocessing import Process, get_context
from multiprocessing.queues import Queue


def start_as_daemon(component_starter_function):
    ok_queue = Queue(ctx=get_context())
    p = Process(target=component_starter_function, kwargs={"ok_queue": ok_queue})
    p.start()
    print(f"{component_starter_function.__name__}... ", end="")
    print(ok_queue.get())