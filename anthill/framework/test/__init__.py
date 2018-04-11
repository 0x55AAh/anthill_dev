import time


class ElapsedTime:
    measures_multiplier_map = {'ms': 1000}

    def __init__(self, name, measure='ms', done_callback=None):
        if measure not in self.measures_multiplier_map:
            raise ValueError('Measure `{}` is not valid'.format(measure))

        self.name = name
        self.measure = measure
        self.start = time.time()
        self.end = None
        self.elapsed = None
        self.done_callback = done_callback

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__done__()

    def __str__(self):
        if self.elapsed:
            multiplier = self.measures_multiplier_map[self.measure]
            return '[{0}] finished in {1} ms'.format(self.name, int(self.elapsed * multiplier))
        return '[{}] not finished yet'.format(self.name)

    def __repr__(self):
        return str(self)

    def __call__(self, *args, **kwargs):
        self.__done__()

    def __done__(self):
        self.done()
        if done_callback is not None:
            if not callable(self.done_callback):
                raise ValueError('`done_callback` must be callable')
            self.done_callback(self)

    def done(self):
        self.end = time.time()
        self.elapsed = self.end - self.start
        return self
