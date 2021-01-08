from multiprocessing import Process, get_context
from multiprocessing.queues import Queue


def start_as_daemon(component_starter_function):
    ok_queue = Queue(ctx=get_context())
    pname = component_starter_function.__name__
    p = Process(target=component_starter_function, kwargs={"ok_queue": ok_queue}, name=pname)
    p.start()
    print(f"{pname}... ", end="")
    print(ok_queue.get())
    return p