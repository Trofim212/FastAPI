from typing import List
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from ..models import Post,UserPostLikes

    

def get_post(post_id:int,db:Session) -> Post:
    post = db.query(Post).get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f'post {post_id} not found')
    return post

def get_post_if_not_owner(
    post_id:int,
    username:str,
    creditional_exc:HTTPException,
    db
    ) -> Post:
    post = get_post(post_id,db)
    if post.username == username:
        raise creditional_exc
    return post

def get_post_if_owner(
    post_id:int,
    username:str,
    creditional_exc:HTTPException,
    db:Session
    ) -> Post:
    post = get_post(post_id,db)
    if post.username != username:
        raise creditional_exc
    return post

def get_associate_table(username,post_id,db:Session) -> UserPostLikes | None:
    upl = db.query(UserPostLikes).filter_by(username=username,post_id=post_id).first()
    return upl

def get_posts_filter_limit(count:int,order_by:str,db:Session,**filter_kwargs) -> List[Post]:
    order_by = getattr(Post,order_by)
    return db.query(Post).filter_by(**filter_kwargs).order_by(order_by).limit(count).all()