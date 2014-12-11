from random import uniform

from enum import Enum


CYRIDE = False


class Logger(object):
    _TOTAL_ITEMS = 0
    LOGGED_INFO = {
        'gruntled': [],
        'sent_messages': {
            'unit_heads': {},
            'madden': [],
        },
    }
    EMPLOYEES = []
    HEADS = []
    MADDEN = None

    LOG = True

    def __init__(self):
        self.id = Logger._TOTAL_ITEMS
        Logger._TOTAL_ITEMS += 1

    def log(self, message):
        if Logger.LOG:
            type_name = ""
            if type(self) is UnitHead:
                type_name = "UH "
            print "{1}{0}: {2}".format(self.id, type_name, message)

    @staticmethod
    def _reset():
        Logger._TOTAL_ITEMS = 0
        Logger.LOGGED_INFO = {
            'gruntled': [],
            'sent_messages': {
                'unit_heads': {},
                'madden': [],
            },
        }
        Logger.EMPLOYEES = []
        Logger.HEADS = []
        Logger.MADDEN = None

        Logger.LOG = True


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
        self.start_distance = distance
        self.intensity = intensity
        self.time = time
        self.speed = float(self.distance) / float(self.time)
        self.state = "arriving"

        self.action = env.process(self.run())

    @staticmethod
    def log(msg):
        if Logger.LOG:
            print msg

    def run(self):
        if self.state == "arriving":
            while self.distance > 0:
                self.distance -= 1
                if self.distance == 0:
                    Weather.log("+-----------------+")
                    Weather.log("| WEATHER ARRIVED |")
                    Weather.log("+-----------------+")
                    self.state = "here"
                yield self.env.timeout(float(self.time) / self.start_distance)
        if self.state == "here":
            while True:
                die = uniform(0, 11)
                if die >= self.intensity:
                    self.state = "clearing"
                    Weather.log("Clearing")
                    break
                yield self.env.timeout(1)
        if self.state == "clearing":
            while True:
                self.distance += 1
                yield self.env.timeout(float(self.time) / self.start_distance)


class Madden(Logger):
    def __init__(self, env, weather, time_to_call, pipes):
        self.env = env
        self.weather = weather
        self.time_to_call = time_to_call
        assert time_to_call < self.weather.time, "Madden must make call before weather arrives."
        self.pipes = pipes

        self.cog_load = 0.0

        Logger.MADDEN = self
        self.action = env.process(self.run())
        super(Madden, self).__init__()
        self.id = 0

    def run(self):
        shutdown = False
        while True:
            if not shutdown:
                time_to_arrival = self.weather.distance / self.weather.speed

                # people are telling him things so his workload is going up
                self.cog_load += uniform(-0.1, self.weather.intensity * 0.1)
                yield self.env.timeout(0.25)

                # he parses that information so his workload goes down
                self.cog_load -= 0.1
                yield self.env.timeout(uniform((1 / 6), 0.5))
                if self.time_to_call <= time_to_arrival and self.env.now < 8:
                    clear_percentage = 1 - ((self.weather.intensity / 11.0) ** (12 - self.weather.time))
                    if clear_percentage < 0.8  and clear_percentage > 0:
                        shutdown = True
                        msg = {
                            "time": self.env.now,
                            "command": "HOME",
                            "kind": "ALL",
                            "quality": "good",
                            "distance": -1,
                            "id": self.id
                        }
                        Logger.LOGGED_INFO['sent_messages']['madden'].append((msg, self.env.now))
                        _ = [pipe.put(msg) for pipe in self.pipes]
                        self.log("SHUTDOWN ({0})".format(self.env.now % 24))
            else:
                yield self.env.timeout(0.1)


class UnitHead(Logger):
    """The unit head object. Is responsible for a department or
    staff unit.

    Args:
        env: The simpy environment.
        weather: The weather instance.
        employees: A list of employee objects.
        name: The name of the unit."""
    def __init__(self, env, weather, initial_workload, pipe):
        self.env = env
        self.weather = weather
        self.pipe = pipe

        self.check_interval = max(0, 1 / min(1.0, float(self.weather.intensity) - 2))
        # check by the inverse of how bad the weather is
        # that is -- if the weather is just bad, check every hour
        # if it's really bad, check every half hour
        # and if it's apocalyptic out there, check every 10 minutes

        self.workload = initial_workload
        # a scaling factor affected by how bad and fast the weather is
        # moving and how much and the quality of the information they're
        # receiving. Affects lots of things, like they're ability to
        # estimate when they should alert employees
        Logger.HEADS.append(self)
        self.action = env.process(self.run())
        super(UnitHead, self).__init__()
        Logger.LOGGED_INFO['sent_messages']['unit_heads'][self.id] = []

    def run(self):
        # sleep and travel
        yield self.env.timeout(8)
        while True:
            # Check the weather
            yield self.env.timeout(self.check_interval)

            minimum = 1 * (self.workload - 0.5)
            if minimum < 0:
                minimum = 0
            #self.workload += uniform(-0.1, (self.weather.distance / self.weather.speed))
            quotient = (self.weather.distance / self.weather.speed) * uniform(minimum, self.workload)
            if quotient < (self.weather.start_distance / self.weather.speed) / 20:
                msg = {
                    "time": self.env.now,
                    "command": "HOME",
                    "kind": "ALL",
                    "quality": "good",
                    "distance": self.weather.distance,
                    "id": self.id
                }
                Logger.LOGGED_INFO['sent_messages']['unit_heads'][self.id].append((msg, self.env.now))
                self.pipe.put(msg)
                self.log("Sent go home message ({0})".format(self.env.now % 24))


class Employee(Logger):
    class location(Enum):
        """Where the employee currently is."""
        home = 0
        work = 1
        traveling = 2

    class kind(Enum):
        """What kind of employee they are."""
        staff = 0
        faculty = 1
        student_worker = 2

    _counter = 0

    def __init__(
        self,
        env,
        weather,
        distance,
        pipe,
        likelihood=1.0,
        speed=45,
        kind=0
    ):
        self.env = env
        self.speed = speed
        self.distance = distance
        self.weather = weather
        self.kind = kind
        self.pipe = pipe
        self.likelihood = likelihood

        self.cog_load = 0.0

        self.location = Employee.location.home
        self.status = None
        self.send_home = False

        self.simulate = True

        # runs every time a new employee is created
        Logger.EMPLOYEES.append(self)
        self.action = env.process(self.run())
        super(Employee, self).__init__()

    def run(self):
        while self.simulate:
            # sleep until 8 AM
            yield self.env.timeout(8)

            # wake up and spend an hour getting ready
            self.log("Waking up at {0}.".format(self.env.now % 24))
            yield self.env.timeout(1)

            # check the weather before we head out...
            self.log("Checking weather.")
            msg = yield self.pipe.get()
            if msg is not None:
                if msg['id'] == 0:
                    if msg['command'] == "HOME":
                        if uniform(0, self.likelihood) <= 0.5:
                            self.log("Following Madden's advice.")
                            self.simulate = False
                            self.status = "MADDEN"
                            break
            else:
                # if the weather will get to work faster than they will
                # then they opt to stay home. more intense weather makes
                # it more likely they'll stay home
                weather_factor = float(self.weather.distance / self.weather.speed) / float(self.weather.intensity)
                personal_factor = (float(self.distance) / self.speed)
                if weather_factor * uniform(0, self.likelihood) < personal_factor and self.weather.state != "clearing":
                    self.log("Staying home.")
                    self.simulate = False
                    self.status = "SELF"
                    break

            # if they're a student worker, cyride is shut down, and they can't walk to work
            # then they can't come in at all
            if self.kind is Employee.kind.student_worker:
                if not CYRIDE and self.distance > 1.0:
                    self.log("Cannot get to work because Cyride is closed.")
                    self.simulate = False
                    self.status = "CYRIDE"
                    break

            # if none of that is true, they travel to work
            self.log("Going to work at {0}.".format(self.env.now % 24))
            yield self.env.process(self._travel(self.distance))
            self.location = Employee.location.work

            # and once they get there, they check their messages once an hour
            self.log("Arrived at work at {0}.".format(self.env.now % 24))
            arrived = self.env.now
            for i in range(8):
                # a worker's cognitive load goes up and down throughout the day
                self.cog_load += uniform(-0.3, 0.3)
                if self.cog_load < 0:
                    self.cog_load = 0

                # if they got a go home message, they have to work to reduce their load
                if self.send_home:
                    if self.cog_load <= 0:
                        yield self.env.process(self.go_home())
                        # removed from the simulation

                        self.simulate = False
                        self.status = "MESSAGE"
                        return
                    else:
                        self.cog_load -= uniform(self.likelihood / 2, min(1.0, self.likelihood + 0.5))
                else:
                    self.log("Checking messages.")
                    # checking the messages, which flips the send_home flag
                    self.env.process(self.check_for_messages(self.pipe, arrived))
                yield self.env.process(self.work(1))

            # at the end of the day, go home
            yield self.env.process(self.go_home())

            # stay at home for the remainder of the day (until midnight, technically)
            self.status = "SLEEP"
            yield self.env.timeout(24 - (self.env.now % 24))
            self.log("Slept until {0}.".format(self.env.now % 24))

    def go_home(self):
        self.log("Leaving work at {0}.".format(self.env.now % 24))
        yield self.env.process(self._travel(self.distance))

        self.location = Employee.location.home
        self.log("Arrived at home at {0}.".format(self.env.now % 24))

    def _travel(self, distance):
        self.location = Employee.location.traveling
        yield self.env.timeout(self.distance / float(self.speed))

    def work(self, duration):
        yield self.env.timeout(duration)

    def check_for_messages(self, in_pipe, arrival_time):
        msg = yield in_pipe.get()
        if "HOME" in msg['command'] and self.location is not Employee.location.home:
            # make sure the message is for you specifically
            if msg['kind'] == "ALL" or Employee.kind[msg['kind']] == self.kind:
                if msg['distance'] < self.distance:
                    # when the weather hits, everyone gets a bump in their load
                    self.cog_load += 0.2
                    self.send_home = True
                    self.log("Received go home message from {0}.".format(msg['id']))
                    # if you get to work and then find out you have to go
                    # home, you're going to be unhappy
                    if msg['time'] < arrival_time + 2:
                        Logger.LOGGED_INFO['gruntled'].append(msg['id'])
                        self.log(">>>> Late message received.")


class Review(Logger):
    @staticmethod
    def get_disgruntled_employees():
        output = {}
        if Logger.LOGGED_INFO.get('gruntled') is None:
            return None
        for disgruntled_id in Logger.LOGGED_INFO['gruntled']:
            output[disgruntled_id] = output.setdefault(disgruntled_id, 0) + 1
        return output

    @staticmethod
    def get_statuses():
        output = {}
        for employee in Logger.EMPLOYEES:
            location = employee.location.name
            output[location] = output.setdefault(location, {})
            output[location][employee.status] = output[location].setdefault(employee.status, 0) + 1
        return output

    @staticmethod
    def get_unit_head_messages():
        output = {'messages': {}, 'first_message': (0, 0)}
        for head_id, messages in Logger.LOGGED_INFO['sent_messages']['unit_heads'].items():
            output['messages'][head_id] = len(messages)
            for message in messages:
                if message[1] < output['first_message']:
                    output['first_message'] = message
        return output
