import json
import time

import spreadsheet

with open('config.json', 'r') as f:
    config = json.load(f)


def get_workout_days_for_range(days_range=7):
    days = spreadsheet.fetch_cells_from_sheet(config['workout_days_sheet_id'], config['workout_days_sheet_range'])
    result = []
    for i in range(len(days)):
        day = time.strptime(days[i], config['date_format'])
        count = 1

        for j in range(i - 1, -1, -1):
            day_earlier = time.strptime(days[j], config['date_format'])
            delta_sec = time.mktime(day) - time.mktime(day_earlier)
            delta_day = int(delta_sec / 24 / 3600)
            if delta_day >= days_range:
                break
            count += 1
        result.append(count)
    return days, result
