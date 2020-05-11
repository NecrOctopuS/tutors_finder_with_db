import data
from app import db
from app import Goal, Teacher


def add_goals():
    for slug, description in data.goals.items():
        goal = Goal(slug=slug, description=description)
        db.session.add(goal)
    db.session.commit()


def add_teachers():
    for profile in data.teachers:

        teacher = Teacher(
            name=profile['name'],
            about=profile['about'],
            rating=profile['rating'],
            picture=profile['picture'],
            price=profile['price'],
            free=profile['free'],
        )
        for profile_goal in profile['goals']:
            goal = db.session.query(Goal).filter(Goal.slug == profile_goal).one()
            teacher.goals.append(goal)
        db.session.add(teacher)
    db.session.commit()


def main():
    add_goals()
    add_teachers()


if __name__ == '__main__':
    main()
