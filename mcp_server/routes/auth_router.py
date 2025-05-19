from fastapi import APIRouter, HTTPException, Request, Depends, Header
from models.user import UserSignupRequest, UserLoginRequest, UserTrackRequest
from mcp_server.services import auth_service
from pydantic import BaseModel
from typing import Optional
import httpx
from datastore.supabase_client import supabase
import logging

router = APIRouter()

# ------------------------------------
# Auth SignUp/Login/Logout Endpoints
# ------------------------------------

@router.post("/auth/signup")
async def signup(user: UserSignupRequest):
    result = auth_service.signup_user(user)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/auth/login")
async def login(user: UserLoginRequest):
    result = auth_service.login_user(user)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/auth/logout")
async def logout():
    result = auth_service.logout_user()
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# ------------------------------------
# User Tracking Endpoint
# ------------------------------------

import os
import httpx
from fastapi import HTTPException, Header

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

async def validate_access_token(authorization: str = Header(...)):
    """
    Validate access token using Supabase /auth/v1/user with API Key fallback.
    This prevents 401 issue due to missing 'apikey' header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.replace("Bearer ", "").strip()

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_ANON_KEY  # Adding apikey header to avoid Supabase strict rejection
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SUPABASE_URL}/auth/v1/user", headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail=f"Invalid or expired access token (Supabase responded {response.status_code})")

    user_data = response.json()

    if not user_data.get("email"):
        raise HTTPException(status_code=401, detail="User email not found in token.")

    return user_data  # This will be injected as user_data in route


# EXAMPLE USAGE in FastAPI router

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UserTrackRequest(BaseModel):
    email: str
    full_name: Optional[str] = None
    provider: Optional[str] = None
    avatar_url: Optional[str] = None

@router.post("/auth/track")
async def track_user(user: UserTrackRequest, user_data=Depends(validate_access_token)):
    try:
        # print("Token Validated User Info:", user_data)

        result = supabase.table("users").insert({
            "email": user.email,
            "full_name": user.full_name,
            "provider": user.provider,
            "avatar_url": user.avatar_url
        }).execute()

        # print("Supabase upsert result:", result)

        if result.status_code not in [200, 201]:
            raise HTTPException(status_code=500, detail="Failed to insert/update user.")

        return {"message": "User tracked successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tracking failed: {str(e)}")


# ========================================================================
# SUPABASE_URL = "https://hvqijjmhhhukoarccqhh.supabase.co"

# async def validate_access_token(request: Request):
#     auth_header = request.headers.get("Authorization")
#     if not auth_header or not auth_header.startswith("Bearer"):
#         raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

#     token = auth_header.split(" ")[1]

#     async with httpx.AsyncClient() as client:
#         res = await client.get(
#             f"{SUPABASE_URL}/auth/v1/user",
#             headers={"Authorization": f"Bearer {token}"}
#         )

#     if res.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

#     return res.json()


# class UserTrackRequest(BaseModel):
#     email: str
#     full_name: Optional[str] = None
#     provider: Optional[str] = None
#     avatar_url: Optional[str] = None

# @router.post("/auth/track")
# async def track_user(user: UserTrackRequest, user_data=Depends(validate_access_token)):
#     try:
#         print("Tracking user: ", user)

#         result = supabase.table("users").upsert({
#             "email": user.email,
#             "full_name": user.full_name,
#             "provider": user.provider,
#             "avatar_url": user.avatar_url
#         }).execute()

#         print("Supabase result:", result)

#         if result.status_code not in [200, 201]:
#             raise HTTPException(status_code=500, detail="Failed to insert/update user.")

#         return {"message": "User tracked successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Tracking failed: {str(e)}")

