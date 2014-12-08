import simpy

from models import Weather, Employee, UnitHead
from messages import BroadcastPipe

env = simpy.Environment()
weather = Weather(
    env=env,
    time=14,
    distance=60,
    intensity=1,
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

head = UnitHead(env, weather, 1.0, bc_pipe)

env.run(until=24)
