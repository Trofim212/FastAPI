from pydantic import BaseModel,EmailStr,constr,Field
from enum import Enum

class UserUsername(BaseModel):
    username : constr(max_length=20,min_length=2)

class UserPassword(BaseModel):
    password : constr(min_length=8,max_length=20)

class UserEmail(BaseModel):
    email : EmailStr
    
    

class UserAuthorize(UserPassword,UserUsername,UserEmail):
    pass

class UserLogin(UserUsername,UserPassword):
    pass

class UserOut(UserUsername,UserEmail):
    pass

class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(UserUsername):
    expire : int

class PostCreate(BaseModel):
    title : str
    body : str

class PostOut(PostCreate):
    username : str
    id : int

class PostOrderEnum(Enum):
    title = 'title'
    body = 'body'
    username = 'username'
    id = 'id'

class MarkEnum(Enum):
    like = 'like'
    dislike = 'dislike'

class Mark(BaseModel):
    post_id : int
    mark : MarkEnum = Field(alias='your_mark')

class MarkOut(BaseModel):
    post : PostOut
    user : UserOut
    mark : str