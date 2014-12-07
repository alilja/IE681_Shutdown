import simpy

from models import Weather, Employee


env = simpy.Environment()
weather = Weather(env, 1, 5, 1)

employees = [
    Employee(
        env=env,
        weather=weather,
        distance=30.0,
        speed=60,
        kind=Employee.kind.staff
    ),
    Employee(
        env=env,
        weather=weather,
        distance=2.0,
        speed=60,
        kind=Employee.kind.student_worker
    ),
    Employee(
        env=env,
        weather=weather,
        distance=0.5,
        speed=60,
        kind=Employee.kind.student_worker
    ),
]

env.run(until=24)
