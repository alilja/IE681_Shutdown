from random import normalvariate, uniform

import simpy

from models import Weather, Employee, UnitHead, Madden, Review
from messages import BroadcastPipe


def build_unit(
    env,
    weather,
    num_employees=10,
    employee_min_distance=0,
    employee_max_distance=60,
    employee_mean_distance=15,
    percent_student=42.5,
    head_workload=None,
):
    employees = []

    pipe = BroadcastPipe(env)
    student_limit = round(percent_student * num_employees)
    for i in range(num_employees):
        kind = Employee.kind.staff
        if i <= student_limit:
            kind = Employee.kind.student_worker
        distance = normalvariate(employee_mean_distance, 15)
        while distance < employee_min_distance or distance > employee_max_distance:
            distance = normalvariate(employee_mean_distance, 15)

        employees.append(Employee(
            env=env,
            weather=weather,
            distance=distance,
            kind=kind,
            pipe=pipe.get_output_conn()
        ))

    if not head_workload:
        head_workload = uniform(0.15, 0.3)
    head = UnitHead(env, weather, head_workload , pipe)
    return (pipe, head, employees)


env = simpy.Environment()
weather = Weather(
    env=env,
    time=8,
    distance=60,
    intensity=4,
)
"""
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

head = UnitHead(env, weather, 0.0, bc_pipe)"""
units = []
for i in range(2):
    units.append(build_unit(env=env, weather=weather, head_workload=0.0))

madden = Madden(env, weather, 1, [unit[0] for unit in units])

env.run(until=24)


disgruntled_employees = Review.get_disgruntled_employees()
for head_id, num in disgruntled_employees.items():
    print "Unit Head #{0} had {1} late notices.".format(head_id, num)

print Review.get_statuses()
print Review.get_unit_head_messages()
