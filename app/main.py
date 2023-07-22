from .routes import auth,post
from fastapi import FastAPI
from . import models,database
from fastapi.openapi.utils import get_openapi

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(post.router)

@app.get('/')
def _():
    return {'ok':True}

def get_custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title='Social network',
        version='1.0.0',
        summary='Social network for creating and liking your posts',
        description='You can authorize and create your posts, rate posts of other people, if they are gives you emotions',
        routes=app.routes
    )
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = get_custom_openapi