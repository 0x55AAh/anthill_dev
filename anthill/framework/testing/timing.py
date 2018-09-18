import time
import logging


default_logger = logging.getLogger('anthill.application')


class ElapsedTime:
    measures_multiplier_map = {'ms': 1000}

    def __init__(self, name, *args, measure='ms', logger=None, **kwargs):
        if measure not in self.measures_multiplier_map:
            raise ValueError('Measure `{}` is not valid'.format(measure))

        self.name = name.format(*args, **kwargs)
        self.measure = measure
        self.start = time.time()
        self.end = None
        self.elapsed = None
        self.logger = logger or default_logger

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug(self.done())

    def __str__(self):
        if self.elapsed:
            multiplier = self.measures_multiplier_map[self.measure]
            return '[{0}] finished in {1} ms'.format(
                self.name, int(self.elapsed * multiplier))
        return '[{}] not finished yet'.format(self.name)

    def __repr__(self):
        return '<ElapsedTime(name={0}, start={1}, end={2})>'.format(
            self.name, self.start, self.end)

    def done(self):
        self.end = time.time()
        self.elapsed = self.end - self.start
        return self
