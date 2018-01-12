import time


class ElapsedTime:
    measures_multiplier_map = {
        'ms': 1000
    }

    def __init__(self, name, measure='ms'):
        if measure not in self.measures_multiplier_map:
            raise ValueError('Measure {} is not valid'.format(measure))

        self.name = name
        self.measure = measure
        self.start = time.time()
        self.end = None
        self.elapsed = None

    def __str__(self):
        if self.elapsed:
            multiplier = self.measures_multiplier_map[self.measure]
            return '[{}] finished in {} ms'.format(self.name, int(self.elapsed * multiplier))
        return '[{}] not finished yet'.format(self.name)

    def __repr__(self):
        return str(self)

    def done(self):
        self.end = time.time()
        self.elapsed = self.end - self.start
        return self
