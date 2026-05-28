from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    allow_methods=["*"]
    allow_headers=["*"]
)

#Base de datos
DATABASE_URL = "sqlite:////data/recipes.db"
engine = create_engine(DATABASE_URL)

# Modelos

class RecipeBase(SQLModel):
    name: str
    category: str
    servings: int
    ingredients: str
    prep_time: int
    description: str
    image: str


class RecipeCreate(RecipeBase): 
    pass

class RecipeResponse(RecipeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    

class RecipeUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    servings: int | None = None
    ingredients: str | None = None
    prep_time: int | None = None
    description: str | None = None
    image: str | None = None

recipes=[]

# Crear las tablas
def create_db():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Welcome to Maui's Recipe API!"}


@app.get("/recipes") 
def get_recipes():
    with Session(engine) as session:
        recipes = session.exec(select(RecipeResponse)).all()
    return recipes


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with Session(engine) as session:
        recipe = session.get(RecipeResponse, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return recipe

@app.post("/recipes")
def create_recipe(recipe: RecipeCreate):
    with Session(engine) as session:
        db_recipe = RecipeResponse.model_validate(recipe) # convierte la info entrante con forma RecipeCreate en info con forma RecipeResponse
        session.add(db_recipe) # Le dices a la db lo que quieres guardar
        session.commit() # Lo guardas en la db
        session.refresh(db_recipe) # Actualizas el objeto que has guardado para que el id pase de none a tener un valor
        return db_recipe # Devuelve la receta con el id ya generado
   

@app.put("/recipes/{recipe_id}")
def update_recipe(recipe_id: int, updated_recipe: RecipeCreate):
    with Session(engine) as session:
        recipe = session.get(RecipeResponse, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe_data = updated_recipe.model_dump()
        for key, value in recipe_data.items():
            setattr(recipe, key, value)
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe

@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
   with Session(engine) as session:
       recipe = session.get(RecipeResponse, recipe_id)
       if not recipe:
           raise HTTPException(status_code=404, detail="Recipe not found")
       session.delete(recipe)        
       session.commit()
       return {"message":"Recipe deteled"}

@app.patch("/recipes/{recipe_id}")
def patch_recipe(recipe_id: int, updated_recipe: RecipeUpdate):
    with Session(engine) as session:
        recipe = session.get(RecipeResponse, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe_data = updated_recipe.model_dump(exclude_none=True)
        for key, value in recipe_data.items():
            setattr(recipe, key, value)
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
        return recipe


