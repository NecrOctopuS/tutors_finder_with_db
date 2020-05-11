import json
import random

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


def read_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    if contents:
        return json.loads(contents)
    return []


def write_json(json_path, data):
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)


def get_profile_from_json_by_id(id, json_path):
    profiles = read_json(json_path)
    for profile in profiles:
        if profile['id'] == id:
            return profile


def get_profile_goals(profile, json_path):
    goals = read_json(json_path)
    profile_goals = []
    for goal in profile['goals']:
        profile_goals.append(goals[goal])
    return profile_goals


def get_free_profile_hours(schedule):
    free_hours = {}
    for day, hours in schedule.items():
        day_hour = {}
        for hour, possibility in hours.items():
            if possibility:
                day_hour[hour] = possibility
        free_hours[day] = day_hour
    return free_hours


def write_lesson_to_json(id, weekday, time, json_path):
    profiles = read_json(json_path)
    for profile in profiles:
        if profile['id'] == id:
            profile['free'][weekday][time] = False
            break
    write_json(json_path, profiles)


def get_goals_for_request_form(json_path):
    goals = read_json(json_path)
    return [(key, value) for key, value in goals.items()]


def write_request_to_json(goal, time, name, phone, json_path):
    requests = read_json(json_path)
    requests.append({
        'goal': goal,
        'time': time,
        'name': name,
        'phone': phone,
    })
    write_json(json_path, requests)

