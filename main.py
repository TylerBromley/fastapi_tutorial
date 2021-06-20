from enum import Enum
from typing import List, Optional, Set

from fastapi import Body, Cookie, FastAPI, Header, Path, Query
from pydantic import BaseModel, EmailStr, Field, HttpUrl

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float = 10.5
    tags: List[str] = []
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

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None




app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar Fighters", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": "There goes my baz", "price": 50.2, "tax": 10.5,},
}

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
    ads_id: Optional[str] = Cookie(None),
    q: Optional[str] = Query(
        None,
        title="Query string",
        min_length=3,
        max_length=50,
        description="Query string for the items to search in the database " +
        "that have a good match",
        # regex="^fixedquery$",
    ),
    user_agent: Optional[str] = Header(None),
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if user_agent:
        results.update({"User-Agent": user_agent})
    if ads_id:
        results.update(({"ads_id": ads_id}))
    if q:
        results.update({"q": q})
    return results

# the function param q will be optional, and None by default
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item_id(item_id: str):
    return items[item_id]

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]

@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]

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

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

@app.post("/offers")
async def create_offer(offer: Offer):
    return offer

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user



########## PUT ##########

# Declare body, path and query params, all at the same time.
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


