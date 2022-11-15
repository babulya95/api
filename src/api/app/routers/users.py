"""
    Users API router.
    Provides API methods (routes) for working with users.
"""

from app.services.api.response import api_error, ApiErrorCode, api_success
from app.services.request.auth import query_auth_data_from_request
from app.database.dependencies import get_db, Session
from app.serializers.user import serialize_user, serialize_users
from app.database import crud
from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/users/me")
async def method_users_me(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """Returns id, email for current user."""
    auth_data = query_auth_data_from_request(req, db)
    
    return api_success(serialize_user(db, auth_data.user))


@router.get("/users/me/courses")
async def method_users_me_courses(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """Returns list of your courses."""
    auth_data = query_auth_data_from_request(req, db)
    
    purchased_courses = crud.user_course.get_by_user_id(db, user_id=auth_data.user_id)
    return api_success({
        "courses": [],
        "total": len(purchased_courses)
    })


@router.get("/users/list")
async def method_users_list(req: Request, db: Session = Depends(get_db)) -> JSONResponse:
    """Returns list of all users (Permitted only)."""

    auth_data = query_auth_data_from_request(req, db)
    if not auth_data.user.is_admin:
        return api_error(ApiErrorCode.API_FORBIDDEN, "You have no access to call this method!")
    
    users = crud.user.get_all(db)
    return api_success({
        **serialize_users(db, users),
        "total": len(users)
    })
