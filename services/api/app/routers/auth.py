"""Auth endpoints (dev: pick a seeded user to sign in as)."""
from fastapi import APIRouter, Depends, HTTPException

from .. import auth
from ..models import AuthUser, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def do_login(req: LoginRequest) -> LoginResponse:
    try:
        token, user = auth.login(req.username)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"unknown user {req.username}")
    return LoginResponse(token=token, user=AuthUser(**user))


@router.get("/me", response_model=AuthUser)
def me(user: dict = Depends(auth.current_user)) -> AuthUser:
    return AuthUser(**user)


@router.get("/users", response_model=list[AuthUser])
def users() -> list[AuthUser]:
    return [AuthUser(**u) for u in auth.USERS.values()]
