import time


class Throttler:

    def __init__(self, seconds_per_iteration):
        self.seconds_per_iteration = seconds_per_iteration
        self.start_time = time.time()
        self.i = 0

    def wait_for_iteration(self):
        required_time = self.i * self.seconds_per_iteration
        time_elapsed = time.time() - self.start_time
        if required_time > time_elapsed:
            time.sleep(required_time - time_elapsed)
        self.i += 1
