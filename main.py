from enum import Enum
from typing import List, Optional, Set

from fastapi import Body, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: Set[str] = set()
    image: Optional[List[Image]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
                "tags": [],
                "image": [
                    {
                        "url": "string",
                        "name": "string"
                    }
                ]
            }
        }

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[Item]

class User(BaseModel):
    username: str
    full_name: Optional[str] = None



app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

"""
Declaring other function params that are not part of the path params,
they are automatically interpreted as "query" params. 

Multiple paths
and query parameters can be declared at the same time and FastAPI
knows which is which. No specific order is required.

If query param required, don't declare a default value
"""
########## GET ##########

@app.get("/")
async def root():
    return {"message": "Welcome Home!"}

# Optional[str] = Query(None, some_other_arg) makes Query optional,
# using ... as the first arg in query means it is required
@app.get("/items/")
async def read_items(
    q: Optional[str] = Query(
        None,
        title="Query string",
        min_length=3,
        max_length=50,
        description="Query string for the items to search in the database " +
        "that have a good match",
        # regex="^fixedquery$",
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results

# the function param q will be optional, and None by default
@app.get("/items/{item_id}")
async def read_item_id(
    item_id: int = Path(..., title="The ID of the item to get"),
    q: Optional[str] = Query(None, alias="item-query")
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}/items/{items_id}")
async def read_user_item(
    user_id: int, item_id: str, needy: str, q: Optional[str] = None, short: bool = False
):
    item = {"item_id": item_id, "needy": needy, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item



@app.get("/models/{model_name}")
# Declare path parameter with a type annotation using the enum class ModelName
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

# PATH CONVERTER
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}

########## POST ##########

@app.post("/images/multiple/")
async def create_multiple_images(images: List[Image]):
    return images

@app.post("/items/")
async def create_item(item: Item):
    # update the model with price + tax
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.post("/offers")
async def create_offer(offer: Offer):
    return offer



########## PUT ##########

# Declare body, path and query params, all at the same time.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


