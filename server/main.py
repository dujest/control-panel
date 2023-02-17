from pydantic import BaseModel, validator
import shelve
from typing import List
from fastapi import FastAPI, Path
import time

db = {
    "parameters": {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0},
    "component_types": ["a", "b", "c"],
    "panels": {
        1676121800: ["A_a", "B_b", "C_c", "A_a", "B_b", "C_c", "A_a", "B_b", "C_c"]
    }
}


class Grid(BaseModel):
    items: List[str]

    @validator('items')
    def length_validation(cls, config):
        if len(config) != 9:
            raise ValueError("The list must have 9 elements")

        for element in config:
            if len(element) != 3:
                raise ValueError("All elements in the list must have length 3")

            if element[0] != "o" and element[0] != "O":
                if element[0] not in db["parameters"].keys():
                    raise ValueError("The parameter value is wrong")

                if element[1] != "_":
                    raise ValueError("The binding value is wrong")

                if element[-1] not in db["component_types"]:
                    raise ValueError("The component value is wrong")

            elif element != "off":
                raise ValueError("The off state should be writen as 'off'")

        return config


class Param(BaseModel):
    value: int
    @validator('value')
    def length_validation(cls, val):
        if not -100 <= val <= 100:
            raise ValueError("The value must be in the interval from -100 to 100")
        return val


app = FastAPI()
# get all parameters
@app.get("/parameters")
async def getParameters():
    return db["parameters"]


# change parameter value
@app.put("/parameters/{param_id}")
async def editParameter(*, param_id: str = Path(None, description="The id of parameter you want to change"), val: Param):
    if param_id not in db["parameters"]:
        return {"Error": "Parameter does not exist"}
    db["parameters"].update({param_id: val.value})
    return {"Message": "Parameter updated successfully"}


# get all panels
@app.get("/")
async def getPanels():
    return db["panels"]


# create panel
@app.post("/")
async def createPanel(panel: Grid):
    timestamp = int(time.time())
    db["panels"].update({timestamp: panel.items})
    return db["panels"][timestamp]


# get panel
@app.get("/{panel_id}")
async def getPanel(panel_id: int = Path(None, description="The timestamp of panel you want to use", gt=0)):
    if db["panels"][panel_id]:
        return db["panels"][panel_id]
    return {"Error": "Not found!"}


# edit panel
@app.put("/{panel_id}")
async def editPanel(*, panel_id: int = Path(None, description="The timestamp of panel you want to edit"), panel: Grid):
    if panel_id not in db["panels"]:
        return {"Error": "Panel does not exist"}
    db["panels"].update({panel_id: panel.items})
    return db["panels"][panel_id]


# delete panel
@app.delete("/{panel_id}")
async def deletePanel(panel_id: int = Path(None, description="The timestamp of panel you want to delete")):
    if panel_id not in db["panels"]:
        return {"Error": "Panel does not exist"}
    del db["panels"][panel_id]
    return {"Message": "Panel deleted succesfully"}