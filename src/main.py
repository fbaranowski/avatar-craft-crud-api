from fastapi import FastAPI
from gql_schema import graphql_app
from db_engine import engine
from models import Base

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.add_route('/graphql', graphql_app)
app.add_websocket_route('/graphql', graphql_app)
