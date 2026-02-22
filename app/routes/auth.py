from fastapi import APIRouter, HTTPException, Depends
from app.models.models import UserRegister, UserLogin
from app.config.database import users_collection
from app.auth.jwt import hash_password, verify_password, create_access_token, get_current_user
from app.schemas.schemas import user_serial

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=201)
async def register(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["role"] = "user"

    result = users_collection.insert_one(user_dict)
    return {"message": "User registered successfully", "id": str(result.inserted_id)}


@router.post("/login")
async def login(credentials: UserLogin):
    user = users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user["_id"]), "role": user.get("role", "user")})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return user_serial(current_user)
