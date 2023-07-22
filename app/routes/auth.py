from fastapi import APIRouter,Depends,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schemas,oath2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth',tags=['auth'])

@router.post('/register',response_model=schemas.UserOut,status_code=status.HTTP_201_CREATED)
def create_user(
    user : schemas.UserAuthorize,
    db : Session = Depends(get_db)
    ):
    user = oath2.authorize_user(user,db)
    return schemas.UserOut(email=user.email,username=user.username)

@router.post('/token')
def login_for_access_token(
    user : OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(get_db)
    ):
    user = oath2.authenticate_user(user.username,user.password,db)
    token = oath2.create_access_token({'username':user.username})
    return token