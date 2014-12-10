import simpy

from models import Weather, Madden, Review
import factories

all_logged_info = []

unit_factors = []
for i in range(2):
    unit_factors.append(factories.build_factors(head_workload=0.0))

for i in range(3):
    env = simpy.Environment()
    weather = Weather(
        env=env,
        time=18,
        distance=60,
        intensity=4,
    )
    units = []
    for factors in unit_factors:
        units.append(factories.build_unit(env, weather, factors))
    madden = Madden(env, weather, 1, [unit[0] for unit in units])

    env.run(until=24)

    all_logged_info.append({
        'gruntled': Review.get_disgruntled_employees(),
        'statuses': Review.get_statuses(),
        'messages': Review.get_unit_head_messages(),
    })

    this = all_logged_info[-1]
    print this['gruntled']
    print this['statuses']
    print this['messages']
    print "-" * 80



