import time


def print_time(f):
    """Decorator of viewing function runtime.
    eg:
        ```py
        from print_time import print_time as pt
        @pt
        def work(...):
            print('work is running')
        word()
        # work is running
        # --> RUN TIME: <work> : 2.8371810913085938e-05
        ```
    """
    def fi(*args, **kwargs):
        s = time.time()
        res = f(*args, **kwargs)
        print('--> RUN TIME: <%s> : %s' % (f.__name__, round(float(time.time() - s), 2)))
        return res
    return fi
