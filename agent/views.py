from user.models import User
from .schedule_agent import ScheduleAgent
import threading
from config.config import MAX_TIMEOUT
import ctypes
import queue


def async_raise(tid, exctype):
    """Raises an exception in the threads with id tid"""
    if not issubclass(exctype, BaseException):
        raise TypeError("Only types derived from BaseException are allowed")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


class StoppableThread(threading.Thread):
    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def stop(self):
        async_raise(self.get_id(), SystemExit)


def func_to_run(user_input, user, q):
    schedule_agent = ScheduleAgent(user)
    q.put(schedule_agent(user_input))

# Create your views here.
def agent_main(user_input: str, user: User) -> str:
    q = queue.Queue()
    thread = StoppableThread(target=func_to_run, args=(user_input, user, q))
    # return schedule_agent(user_input)
    thread.start()
    thread.join(MAX_TIMEOUT)
    if thread.is_alive():
        thread.stop()
        raise TimeoutError(f"Timeout after {MAX_TIMEOUT} seconds.")
    else:
        return q.get()
