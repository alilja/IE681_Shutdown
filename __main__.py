#!/usr/bin/env python
import csv

import simpy

from models import Weather, Madden, Review, Logger
import factories


def weather_differences(weather_factors, unit_factors, iterations, start, finish):
    assert start >= 3
    assert finish <= 25
    all_logged_info = [{'TIME': i} for i in range(finish - start)]
    for iteration in range(iterations):
        for i in range(start, finish):
            env = simpy.Environment()
            weather_factors['time'] = i
            weather = Weather(env=env, **weather_factors)
            Logger._reset()
            Logger.LOG = False

            units = []
            for factors in unit_factors:
                units.append(factories.build_unit(env, weather, factors))
            _ = Madden(env, weather, 2, [unit[0] for unit in units])

            env.run(until=24)

            this = all_logged_info[i - start]
            for status, num in Review.get_statuses()['home'].items():
                this[status] = this.get(status, 0) + num

    return all_logged_info

def unit_head_workloads(weather_factors, unit_factors, iterations):
    all_logged_info = [{'WORKLOAD': i} for i in range(10)]
    for i in range(iterations)
        for workload_iteration in range(20):
            env = simpy.Environment()
            weather = Weather(env=env, **weather_factors)
            Logger._reset()
            Logger.LOG = False

            units = []
            for factors in unit_factors:
                factors['head_workload'] = workload_iteration / 20.0
                units.append(factories.build_unit(env, weather, factors))
            _ = Madden(env, weather, 2, [unit[0] for unit in units])

            env.run(until=24)

            this = all_logged_info[i]
            gruntled = Review.get_disgruntled_employees()
            for head_id, num in gruntled.items():
                this[head_id] = num
    return all_logged_info

weather_factors = {
    'time': 8.5,
    'distance': 60,
    'intensity': 8,
}

unit_factors = []
for i in range(2):
    unit_factors.append(factories.build_factors(head_workload=1.0, num_employees=10))

"""Logger._reset()
env = simpy.Environment()
weather = Weather(env=env, **weather_factors)
units = []
for factors in unit_factors:
    units.append(factories.build_unit(env, weather, factors))
_ = Madden(env, weather, 1, [unit[0] for unit in units])

env.run(until=24)

disgruntled_employees = Review.get_disgruntled_employees()
for head_id, num in disgruntled_employees.items():
    print "Unit Head #{0} had {1} late notices.".format(head_id, num)

print Review.get_statuses()
print Review.get_unit_head_messages()"""

workload_delays = unit_head_workloads(weather_factors, unit_factors, 10)
print workload_delays

# weather_messages = weather_differences(weather_factors, unit_factors, 10, 3, 17)
# with open('../data/weather_messages_{0}_cyride.csv'.format(weather_factors['intensity']), 'w') as file:
#    writer = csv.DictWriter(file, ['TIME', 'MESSAGE', 'SLEEP', 'MADDEN', 'SELF', 'CYRIDE'])
#    writer.writeheader()
#    writer.writerows(weather_messages)
