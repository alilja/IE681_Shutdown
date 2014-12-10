from random import normalvariate, uniform

from models import Employee, UnitHead
from messages import BroadcastPipe


def build_factors(
    num_employees=10,
    employee_min_distance=0,
    employee_max_distance=60,
    employee_mean_distance=15,
    percent_student=42.5,
    head_workload=None,
):
    distances = []
    for i in range(num_employees):
        distance = normalvariate(employee_mean_distance, 15)
        while distance < employee_min_distance or distance > employee_max_distance:
            distance = normalvariate(employee_mean_distance, 15)
        distances.append(distance)

    if head_workload is None:
        head_workload = uniform(0.15, 0.3)

    return {
        'num_employees': 10,
        'percent_student': 42.5,
        'distance': distances,
        'head_workload': head_workload,
    }


def build_unit(env, weather, factors):
    employees = []

    pipe = BroadcastPipe(env)
    student_limit = round(factors['percent_student'] * factors['num_employees'])
    for i in range(factors['num_employees']):
        kind = Employee.kind.staff
        if i <= student_limit:
            kind = Employee.kind.student_worker

        employees.append(Employee(
            env=env,
            weather=weather,
            distance=factors['distance'][i],
            kind=kind,
            pipe=pipe.get_output_conn()
        ))

    head = UnitHead(env, weather, factors['head_workload'], pipe)
    return (pipe, head, employees)
