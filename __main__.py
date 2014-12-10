#!/usr/bin/env python

import simpy

from models import Weather, Madden, Review, Logger
import factories

all_logged_info = []

unit_factors = []
for i in range(3):
    unit_factors.append(factories.build_factors(head_workload=0.0))

for i in range(5):
    env = simpy.Environment()
    weather = Weather(
        env=env,
        time=8,
        distance=60,
        intensity=4,
    )
    Logger._reset()
    units = []
    for factors in unit_factors:
        units.append(factories.build_unit(env, weather, factors))
    madden = Madden(env, weather, 2, [unit[0] for unit in units])
    print Logger._TOTAL_ITEMS

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


def get_status(iteration, keyword):
    return iteration['statuses'].get('home', {}).get(keyword, 0)

madden_total = 0
message_total = 0
self_total = 0
none_total = 0
for iteration in all_logged_info:
    print get_status(iteration, 'MADDEN')
    print get_status(iteration, 'MESSAGE')
    print get_status(iteration, 'SELF')
    print get_status(iteration, 'SLEEP')
    print ""

print madden_total, message_total, self_total, none_total