from datastore.supabase_client import supabase
from models.user import UserSignupRequest, UserLoginRequest

def signup_user(user: UserSignupRequest):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password
        })
        if response.user:
            return {"message": "Signup successful", "user_email": response.user.email}
        else:
            return {"error": "Signup failed, check Supabase logs."}
    except Exception as e:
        return {"error": str(e)}

def login_user(user: UserLoginRequest):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        if response.session:
            return {"message": "Login successful", "access_token": response.session.access_token}
        else:
            return {"error": "Login failed, check credentials."}
    except Exception as e:
        return {"error": str(e)}

def logout_user():
    try:
        supabase.auth.sign_out()
        return {"message": "Logout successful"}
    except Exception as e:
        return {"error": str(e)}
