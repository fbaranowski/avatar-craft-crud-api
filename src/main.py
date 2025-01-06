from fastapi import FastAPI

from database.db_engine import engine
from interface.gql_schema import graphql_app
from models import Base

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
