from fastapi import FastAPI

from interface.gql_schema import graphql_app

app = FastAPI()


app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
