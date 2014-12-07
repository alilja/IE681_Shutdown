import simpy

from models import Weather, Employee
from messages import BroadcastPipe


def message_generator(name, env, out_pipe):
    """A process which randomly generates messages."""
    while True:
        # wait for next transmission
        yield env.timeout(5)

        # messages are time stamped to later check if the consumer was
        # late getting them.  Note, using event.triggered to do this may
        # result in failure due to FIFO nature of simulation yields.
        # (i.e. if at the same env.now, message_generator puts a message
        # in the pipe first and then message_consumer gets from pipe,
        # the event.triggered will be True in the other order it will be
        # False

        msg = {
            "time": env.now,
            "command": "HOME",
            "kind": "student_worker",
            "quality": "good",
        }
        print "Message sent at {0}".format(env.now)
        out_pipe.put(msg)

env = simpy.Environment()
weather = Weather(
    env=env,
    time=10,
    distance=20,
    intensity=6,
)

bc_pipe = BroadcastPipe(env)
employees = [
    Employee(
        env=env,
        weather=weather,
        distance=30.0,
        kind=Employee.kind.staff,
        pipe=bc_pipe.get_output_conn(),
    ),
    Employee(
        env=env,
        weather=weather,
        distance=2.0,
        speed=60,
        kind=Employee.kind.student_worker,
        pipe=bc_pipe.get_output_conn(),
    ),
    Employee(
        env=env,
        weather=weather,
        distance=0.5,
        speed=60,
        kind=Employee.kind.student_worker,
        pipe=bc_pipe.get_output_conn(),
    ),
    Employee(
        env=env,
        weather=weather,
        distance=30,
        speed=60,
        kind=Employee.kind.staff,
        pipe=bc_pipe.get_output_conn(),
    ),
]

env.process(message_generator('Generator A', env, bc_pipe))

env.run(until=24)
