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
        """Where the employee currently is."""
        home = 0
        work = 1
        traveling = 2

    class kind(Enum):
        """What kind of employee they are."""
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

        self.send_home = False
        self.gruntled = None

        self.simulate = True

        # runs every time a new employee is created
        self.action = env.process(self.run())

    def run(self):
        while self.simulate:
            # sleep until 8 AM
            yield self.env.timeout(8)

            # wake up and spend an hour getting ready
            print "{0}: Waking up at {1}.".format(self.id, self.env.now % 24)
            yield self.env.timeout(1)

            # check the weather before we head out...
            print "{0}: Checking weather.".format(self.id)
            # if the weather will get to work faster than they will
            # then they opt to stay home. more intense weather makes
            # it more likely they'll stay home
            if (self.weather.distance / self.weather.speed) / self.weather.intensity < self.distance / self.speed:
                print "{0}: Staying home.".format(self.id)
                self.simulate = False
                break

            # if they're a student worker, cyride is shut down, and they can't walk to work
            # then they can't come in at all
            if self.kind is Employee.kind.student_worker:
                if not CYRIDE and self.distance > 1.0:
                    print "{0}: Cannot get to work because Cyride is closed.".format(self.id)
                    self.simulate = False
                    break

            # if none of that is true, they travel to work
            print "{0}: Going to work at {1}.".format(self.id, self.env.now % 24)
            yield self.env.process(self._travel(self.distance))
            self.location = Employee.location.work

            # and once they get there, they check their messages once an hour
            print "{0}: Arrived at work at {1}.".format(self.id, self.env.now % 24)
            arrived = self.env.now
            for i in range(8):
                print "{0}: Checking messages.".format(self.id)
                # checking the messages, which flips the send_home flag
                yield self.env.process(self.check_for_messages(self.pipe, arrived))
                if self.send_home:
                    print "{0}: Received go home message.".format(self.id)
                    # if you get the message to go home, do it
                    yield self.env.process(self.go_home())
                    # removed from the simulation
                    self.simulate = False
                    return
                yield self.env.process(self.work(1))

            # at the end of the day, go home
            yield self.env.process(self.go_home())

            # stay at home for the remainder of the day (until midnight, technically)
            yield self.env.timeout(24 - self.env.now % 24)
            print "{0}: Slept until {1}.".format(self.id, self.env.now % 24)

    def go_home(self):
        print "{0}: Leaving work at {1}.".format(self.id, self.env.now % 24)
        yield self.env.process(self._travel(self.distance))

        self.location = Employee.location.home
        print "{0}: Arrived at home at {1}".format(self.id, self.env.now % 24)

    def _travel(self, distance):
        self.location = Employee.location.traveling
        yield self.env.timeout(distance / self.speed)

    def work(self, duration):
        yield self.env.timeout(duration)

    def check_for_messages(self, in_pipe, arrival_time):
        msg = yield in_pipe.get()

        if "HOME" in msg['command']:
            # make sure the message is for you specifically
            if Employee.kind[msg['kind']] == self.kind or Employee.kind[msg['kind']] == "ALL":
                self.send_home = True
                # if you get to work and then find out you have to go
                # home, you're going to be unhappy
                if msg['time'] < arrival_time + 3:
                    print ">>>> {0}: Late message received.".format(self.id)
                    self.gruntled = "dis"
