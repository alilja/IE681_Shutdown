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
        print iteration
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


weather_factors = {
    'time': 17,
    'distance': 60,
    'intensity': 1,
}

unit_factors = []
for i in range(3):
    unit_factors.append(factories.build_factors(head_workload=0.0))


weather_messages = weather_differences(weather_factors, unit_factors, 10, 3, 20)

print weather_messages

with open('../data/weather_messages_{0}.csv'.format(weather_factors['intensity']), 'w') as file:
    writer = csv.DictWriter(file, ['TIME', 'MESSAGE', 'SLEEP', 'MADDEN', 'SELF'])
    writer.writeheader()
    writer.writerows(weather_messages)

for i, message in enumerate(weather_messages):
    print i + 3, message