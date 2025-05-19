from fastapi import APIRouter, Request, HTTPException, Depends
import httpx

router = APIRouter()

SUPABASE_URL = "https://hvqijjmhhhukoarccqhh.supabase.co"

async def validate_access_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.split(" ")[1]

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}"}
        )

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return res.json()

@router.get("/agent/protected")
async def protected_route(user_data=Depends(validate_access_token)):
    return {"response": f"Hello {user_data['email']}, this is protected data"}
