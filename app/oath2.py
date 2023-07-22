from jose import jwt,JWTError
from passlib.context import CryptContext
from .config import settings
from . import schemas,models
from .database import get_db
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordBearer

oath2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


crypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

def get_hash_password(password : str):
    return crypt_context.hash(password)

def verify_password(plain_password:str,hash_password:str):
    return crypt_context.verify(plain_password,hash_password)

def get_user_by_username(username,db:Session=Depends(get_db)) -> models.User | None:
    user =  db.query(models.User).get(username)
    return user

def get_exception_if_not_username(username,db:Session):
    user = get_user_by_username(username,db)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f'user with username = {username} does not exist')
    return user

def check_user(username,email,creditional_exception:HTTPException,db):
    """
    checks user creditionals for registration process, raise error if input usrename or email
    already exists in database
    """
    check_username = db.query(models.User.username).filter_by(username=username).first()
    if check_username is not None:
        raise creditional_exception
    check_email = db.query(models.User.email).filter_by(email=email).first()
    if check_email is not None:
        raise creditional_exception

def authorize_user(user : schemas.UserAuthorize,db:Session):
    """cheks user creditionals, hashes password and save user in database"""
    creditional_exception = HTTPException(status.HTTP_401_UNAUTHORIZED,'user with this username or email already exists')
    check_user(user.username,user.email,creditional_exception,db)
    
    hash_password = get_hash_password(user.password)
    user_db = models.User(username=user.username,password=hash_password,email=user.email)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return user_db

def authenticate_user(username,password,db:Session)-> models.User:
    """check user creditionals,like username and password in getting token process"""
    user = get_exception_if_not_username(username,db)
    if not verify_password(password,user.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail='incorect password')
    return user

def create_access_token(data: dict):
    """generate jwt token, return Token pydantic class"""
    from time import time
    
    to_encode = data.copy()
    expire = settings.access_token_expires_minutes * 30 + int(time()) 
    to_encode.update({'expire':expire})
    token = jwt.encode(to_encode,settings.secret_key,settings.hash_algorithm)
    token = schemas.Token(access_token=token,token_type='bearer')
    return token

def verify_acces_token(token:str,creditional_exception:HTTPException):
    try:
        payload = jwt.decode(token,settings.secret_key,[settings.hash_algorithm])
        username = payload.get('username')
        expire = payload.get('expire')
        if None in (username,expire):
            raise creditional_exception
        token_data = schemas.TokenData(username=username,expire=expire)
        return token_data
    except JWTError:
        raise creditional_exception

def get_current_user(
    token:str=Depends(oath2_scheme),
    db:Session = Depends(get_db)
    ) -> models.User:
    """if user token is not valid, get http exception
    401_UNAUTHORIZED, else return token data"""
    creditional_exception = HTTPException(
    status.HTTP_401_UNAUTHORIZED,'not valid creditionals',headers={'WWW-Authenticate':'Bearer'})
    token_data =  verify_acces_token(token,creditional_exception)
    user = get_exception_if_not_username(token_data.username,db)
    return user