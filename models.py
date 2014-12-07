import simpy
from enum import Enum

CYRIDE = True


class Weather(object):
    """The weather object.

    Args:
        time: How long until the weather arrives
        distance: How far away the weather begins
        intensity: How intense the weather should be. Higher is
            more intense."""

    def __init__(self, env, time, distance, intensity):
        self.env = env
        self.distance = distance
        self.intensity = intensity

        self.speed = float(distance) / float(time)

        self.action = env.process(self.run())

    def run(self):
        while self.distance > 0:
            self.distance -= 1
            yield self.env.timeout(self.speed)


class Employee(object):
    class location(Enum):
        home = 0
        work = 1
        traveling = 2

    class kind(Enum):
        staff = 0
        faculty = 1
        student = 2
        student_worker = 3

    _counter = 0

    def __init__(self, env, weather, distance, pipe, speed=45, kind=0):
        self.env = env
        self.speed = speed
        self.distance = distance
        self.weather = weather
        self.kind = kind
        self.pipe = pipe

        self.id = Employee._counter
        Employee._counter += 1

        self.location = Employee.location.home

        # runs every time a new employee is created
        self.action = env.process(self.run())

    def run(self):
        while True:
            print "{0}: Waking up at {1}.".format(self.id, self.env.now + 8 % 24)
            yield self.env.process(self.check_for_messages(self.pipe))
            yield self.env.timeout(1)

            print "{0}: Checking weather.".format(self.id)
            # the weather will get to work faster than they will
            print self.weather.distance / self.weather.speed
            print self.distance / self.speed
            if (self.weather.distance / self.weather.speed) / self.weather.intensity < self.distance / self.speed:
                print "{0}: Staying home.".format(self.id)
                break

            if self.kind is Employee.kind.student_worker:
                if not CYRIDE and self.distance > 1.0:
                    print "{0}: Cannot get to work because Cyride is closed.".format(self.id)
                    break

            print "{0}: Going to work at {1}.".format(self.id, self.env.now + 8 % 24)
            yield self.env.process(self.travel(self.distance))

            self.location = Employee.location.work
            print "{0}: Arrived at work at {1}.".format(self.id, self.env.now + 8 % 24)
            for i in range(8):
                yield self.env.process(self.work(1))
                print "{0}: Checking messages.".format(self.id)
                yield self.env.process(self.check_for_messages(self.pipe))

            print "{0}: Leaving work at {1}.".format(self.id, self.env.now + 8 % 24)
            yield self.env.process(self.travel(self.distance))

            self.location = Employee.location.home
            print "{0}: Arrived at home at {1}".format(self.id, self.env.now + 8 % 24)
            yield self.env.timeout(24 - self.env.now)
            print "{0}: Slept until {1}.".format(self.id, self.env.now + 8 % 24)

    def travel(self, distance):
        self.location = Employee.location.traveling
        yield self.env.timeout(distance / self.speed)

    def work(self, duration):
        yield self.env.timeout(duration)

    def check_for_messages(self, in_pipe):
        msg = yield in_pipe.get()
        if msg[0] < self.env.now:
            print "Late message received."

        print "Message: {0}".format(msg[1])
