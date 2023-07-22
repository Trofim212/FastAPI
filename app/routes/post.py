from typing import Annotated, List
from fastapi import APIRouter,Depends,HTTPException,status,Query
from ..import models,schemas,oath2
from ..database import get_db
from sqlalchemy.orm import Session
from . import post_crud

router = APIRouter(prefix='/posts',tags=['posts'])

@router.post('/create',response_model=schemas.PostOut)
def create_post(
    post_data : schemas.PostCreate,
    user : models.User = Depends(oath2.get_current_user),
    db : Session = Depends(get_db)
    ) -> schemas.PostOut:
    
    post = models.Post(**dict(post_data))
    post.username = user.username
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.get('/',response_model=List[schemas.PostOut])
def get_all_posts(
    order_by : schemas.PostOrderEnum = schemas.PostOrderEnum.id,
    count : Annotated[int | None, Query(ge=0,le=50)] = 5,
    db:Session = Depends(get_db)
    ) -> List[models.Post]:

    posts = post_crud.get_posts_filter_limit(count,order_by.value,db)
    return posts

@router.get('/my',response_model=List[schemas.PostOut])
def get_all_my_posts(
    order_by : schemas.PostOrderEnum = schemas.PostOrderEnum.id,
    count : Annotated[int | None, Query(ge=0,le=50)] = 5,
    user : models.User = Depends(oath2.get_current_user),
    db:Session = Depends(get_db)
    ) -> List[models.Post]:
    
    posts = post_crud.get_posts_filter_limit(count,order_by.value,db,username=user.username)
    return posts

@router.post('/mark')
def mark_post(
    mark_data : schemas.Mark,
    user : models.User = Depends(oath2.get_current_user),
    db : Session = Depends(get_db)
    ) -> schemas.MarkOut:
    
    creditional_exc = HTTPException(status.HTTP_409_CONFLICT,'you can not mark your own post')
    is_like = (mark_data.mark.value == 'like')
    post = post_crud.get_post_if_not_owner(mark_data.post_id,user.username,creditional_exc,db)
    mark_db = post_crud.get_associate_table(user.username,mark_data.post_id,db)
    
    if mark_db is None:
        mark_db = models.UserPostLikes(username=user.username,post_id=post.id,like=is_like)
        db.add(mark_db)
    else:
        mark_db.like = is_like
        
    db.commit()
    post_out = schemas.PostOut(title=post.title,body=post.body,username=post.username,id=post.id)
    user_out = schemas.UserOut(username=user.username,email=user.email)
    mark_out = schemas.MarkOut(post=post_out,user=user_out,mark=mark_data.mark.value)
    return mark_out

@router.delete('/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id:int,
    user : models.User = Depends(oath2.get_current_user),
    db : Session = Depends(get_db)
    ) -> None:
    
    creditional_exc = HTTPException(status.HTTP_403_FORBIDDEN,'you can not delete not your own post')
    post = post_crud.get_post_if_owner(id,user.username,creditional_exc,db)
    db.delete(post)
    db.commit()

@router.put('/{id}',response_model=schemas.PostOut)
def update_post(
    id : int,
    post_data : schemas.PostCreate,
    user : models.User = Depends(oath2.get_current_user),
    db : Session = Depends(get_db)
    ) -> models.Post:
    
    creditional_exc = HTTPException(status.HTTP_403_FORBIDDEN,'you can update not your own post')
    post = post_crud.get_post_if_owner(id,user.username,creditional_exc,db)
    post.title = post_data.title
    post.body = post_data.body
    db.commit()
    return post

@router.get('/marked',response_model=List[schemas.PostOut])
def get_my_marked_posts(
    mark : schemas.MarkEnum,
    count : Annotated[int|None, Query(ge=0,lt=50)] = 5,
    user : models.User = Depends(oath2.get_current_user),
    ):
    
    is_like = (mark.value == 'like')
    return user.marked_posts.filter(models.UserPostLikes.like==is_like).limit(count).all()