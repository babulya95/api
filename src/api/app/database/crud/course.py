"""
    Course CRUD utils for the database.
"""

from sqlalchemy.orm import Session
from app.database.models.course import Course, CourseDifficulty


def get_by_id(db: Session, course_id: int) -> Course:
    """Returns course by it`s ID."""
    return db.query(Course).filter(Course.id == course_id).first()


def get_active(db: Session) -> list[Course]:
    """Returns all courses."""
    return db.query(Course).filter(Course.is_active == True).all()


def get_public(db: Session) -> list[Course]:
    """Returns all public courses."""
    return db.query(Course).filter(Course.is_public == True).filter(Course.is_active == True).all()


def create(db: Session, difficulty: CourseDifficulty, owner_id: int, name: str, title: str, description: str = "...", price: int = 0) -> Course:
    """Creates new course."""

    # Create new course.
    course = Course(
        name=name.lower().replace(" ", "-"), 
        difficulty=difficulty.value,
        price=price, 
        owner_id=owner_id, 
        title=title, 
        description=description
    )

    # Apply course in database.
    db.add(course)
    db.commit()
    db.refresh(course)

    return course