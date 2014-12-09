import simpy

from models import Weather, Employee, UnitHead, Review
from messages import BroadcastPipe

env = simpy.Environment()
weather = Weather(
    env=env,
    time=7,
    distance=60,
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

head = UnitHead(env, weather, 0.0, bc_pipe)


env.run(until=24)


disgruntled_employees = Review.get_disgruntled_employees()
for head_id, num in disgruntled_employees.items():
    print "Unit Head #{0} had {1} late notices.".format(head_id, num)

print Review.get_statuses()
print Review.get_unit_head_messages()
