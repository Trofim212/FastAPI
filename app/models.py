from .database import Base
from sqlalchemy import Integer,Column,String,Text,ForeignKey,BOOLEAN
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'users'
    
    username = Column(String(),primary_key=True)
    password = Column(String(),nullable=False)
    email = Column(String(),nullable=False,unique=True)
    
    marked_posts = relationship('Post',secondary='user_post',backref='marking_users',lazy='dynamic')
    
class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer,primary_key=True,autoincrement=True)
    title = Column(String(),nullable=False)
    body = Column(Text,nullable=False)
    username = Column(ForeignKey('users.username',ondelete='SET NULL',onupdate='CASCADE'),nullable=True)

    
class UserPostLikes(Base):
    __tablename__ = 'user_post'
    
    username = Column(ForeignKey('users.username',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,primary_key=True)
    post_id = Column(ForeignKey('posts.id',ondelete='CASCADE',onupdate='CASCADE'),nullable=False,primary_key=True)
    like = Column(BOOLEAN,nullable=False)