from models_dto import UserSchema
from models_db import UserModel
from database import db_session
import secrets

def create_user(user: UserSchema):
    """
    Create a new user and persist it to the database
    """
    # Generate a random password
    random_password = secrets.token_urlsafe(8)
    hashed_password = hash_password(random_password)
    
    # Convert Pydantic model to SQLAlchemy model
    db_user = UserModel(
        email=user.email,
        name=user.name,
        role=user.role,
        password_hash=hashed_password
    )
    
    # Add and commit to database
    db = db_session()
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
    
    # Return response including the clear-text password (one-time reveal)
    response = UserSchema(
        email=user.email,
        name=user.name,
        role=user.role
    )
    
    return response

def authenticate_user(email: str, password: str):
    """
    Authenticate a user by email and password
    """
    db = db_session()
    try:
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            return None
        
        # Check if password matches
        hashed_password = hash_password(password)
        if user.password_hash != hashed_password:
            return None
            
        return user
    finally:
        db.close()

def hash_password(password: str) -> str:
    """
    Hash a password for storing
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest() 