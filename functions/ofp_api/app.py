import os
from typing import Optional, List
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.requests import Request
from utils import transaction
from fastapi.middleware.gzip import GZipMiddleware


app = FastAPI(
    title="Observatório das Florestas API",
    root_path= f"/{os.environ ['STAGE']}/"
)

app.add_middleware(GZipMiddleware)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

@app.get("/mvt/fpnd/{z}/{x}/{y}.pbf", tags=["MVT"])
def get_fpnd_as_mvt(request: Request, response: Response, z: int, x: int, y: int):
    result = transaction.get_fpnd_as_mvt(z,x,y)
    return Response(
        content=result,
        media_type='application/x-protobuf',
        ) 

@app.get("/map-data", tags=["geo"])
def get_map_data(request: Request, response: Response):
    return transaction.get_map_data()

@app.get("/info-data", tags=["geo"])
def get_map_data(request: Request, response: Response,        
    esfera: Optional[str] = Query(None, description="Filtro por esfera administrativa"),
    estados: Optional[List[str]] = Query(None, description="Lista de Unidades Federativas para filtragem"),
    fpnd: Optional[str] = Query(None, description="Filtro por floresta pública não destinada")
):
    return transaction.get_entenda_data(esfera, estados, fpnd)



lambda_handler = Mangum(app)
