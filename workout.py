import json
import time

import spreadsheet

with open('config.json', 'r') as f:
    config = json.load(f)


def get_workout_days_for_range(days_range=7):
    entries = spreadsheet.fetch_cells_from_sheet(config['workout_days_sheet_id'], config['workout_days_sheet_range'])
    result = []

    i = len(entries) - 1
    date = time.localtime()
    date_str = time.strftime(config['date_format'], date)

    while i >= 0:
        count = 0
        for j in range(i - 1, -1, -1):
            day_earlier = time.strptime(entries[j][0], config['date_format'])
            delta_sec = time.mktime(date) - time.mktime(day_earlier)
            delta_day = int(delta_sec / 24 / 3600)
            if delta_day >= days_range:
                break
            count += 1

        if entries[i][0] == date_str:
            count += 1
            data = {'date': date_str, 'count': count, 'workout_day': True, 'weight': float(entries[i][1])}
            i -= 1
        else:
            data = {'date': date_str, 'count': count, 'workout_day': False}
        result.append(data)

        date = time.localtime(time.mktime(date) - 24 * 3600)
        date_str = time.strftime(config['date_format'], date)
    return result
