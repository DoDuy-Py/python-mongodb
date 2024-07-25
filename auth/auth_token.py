from passlib.context import CryptContext
from datetime import datetime, timedelta
from core import settings
from core.base import Response, json_serialize
from datetime import datetime, timezone
import json
from typing import Optional, Dict, Any

# from views_func.function import format_response_data
from core.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

from jose import JWTError, jwt
# >>> token = jwt.encode({'key': 'value'}, 'secret', algorithm='HS256')
# u'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJ2YWx1ZSJ9.FG-8UppwHaFp1LgRYQQeS6EDQF7_6-bMFegNucHjmWg'

# >>> jwt.decode(token, 'secret', algorithms=['HS256'])
# {u'key': u'value'}

def create_access_token(user: any) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
        # seconds=10000
    )
    to_encode = {
        "exp": expire, "user": json.dumps(user, default=json_serialize)
    }
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.SECURITY_ALGORITHM)
    return token

def validate_token(auth: str) -> Optional[Dict[str, Any]]:
    try:
        token = auth.split(" ")[1]  # Lấy token từ header 'Bearer <token>'
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM])
            user = payload.get("user")
            exp = payload.get("exp")
            if not user or not exp:
                raise ValueError("Token is missing user or exp")
            elif datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
                raise ValueError("Token has expired")
            
            return user  # Trả về đối tượng người dùng dưới dạng dictionary (Python dict)
        except JWTError as e:
            print(e)
            raise ValueError(f"JWT Error: {e}")
    except Exception as e:
        print(e)
        raise ValueError(f"Unexpected error: {e}")

def refresh_access_token(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM])
        user = payload.get("user")
        if not user:
            raise ValueError("Token is missing user")
        
        new_access_token = create_access_token(user)
        return new_access_token
    
    except JWTError as e:
        print(e)
        raise ValueError(f"Unexpected error: {e}")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)