from pydantic import BaseModel


class RegisterRequest(BaseModel):
    login: str
    password: str
    first_name: str | None = None
    last_name: str | None = None


class DisplayableUserResponse(BaseModel):
    login: str
    first_name: str | None = None
    last_name: str | None = None


class TokenData(BaseModel):
    access_token: str
    refresh_token: str


class AuthResponse(BaseModel):
    user: DisplayableUserResponse
    token_data: TokenData
