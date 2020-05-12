
WEEKDAYS = {
    "mon": 'Понедельник',
    "tue": 'Вторник',
    "wed": 'Среда',
    "thu": 'Четверг',
    "fri": 'Пятница',
    "sat": 'Суббота',
    "sun": 'Воскресенье'
}

ICONS = {
    "travel": "⛱",
    "study": "🏫",
    "work": "🏢",
    "relocate": "🚜",
    "programming": "🎮"
}


def get_free_profile_hours(schedule):
    free_hours = {}
    for day, hours in schedule.items():
        day_hour = {}
        for hour, possibility in hours.items():
            if possibility:
                day_hour[hour] = possibility
        free_hours[day] = day_hour
    return free_hours
