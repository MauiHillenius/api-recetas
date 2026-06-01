from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime



#Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///recipes.db")
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
    isFav: Optional[bool] = Field(default=False)
    last_visited_at: Optional[datetime] = Field(default=None)
    

class RecipeUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    servings: int | None = None
    ingredients: str | None = None
    prep_time: int | None = None
    description: str | None = None
    image: str | None = None
    isFav: bool | None = None

recipes=[]

# Crear las tablas
def create_db():
    SQLModel.metadata.create_all(engine)

def seed_recipes():
      with Session(engine) as session:
          existing = session.exec(select(RecipeResponse)).first()
          if existing:
              return
          recipes = [
              RecipeResponse(
                  name="Tortilla española",
                  category="Desayuno",
                  servings=4,
                  ingredients="6 huevos, 3 patatas, 1 cebolla, aceite de oliva, sal",
                  prep_time=30,
                  description="La clásica tortilla española con patatas y cebolla pochada.",
                  image="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Tortilla_de_patatas.jpg/640px-Tortilla_de_patatas.jpg",
                  isFav=False
              ),
              RecipeResponse(
                  name="Gazpacho andaluz",
                  category="Entrante",
                  servings=6,
                  ingredients="1kg tomates, 1 pepino, 1 pimiento verde, 1 diente de ajo, aceite, vinagre, sal",
                  prep_time=15,
                  description="Sopa fría de verduras típica del verano andaluz.",
                  image="https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Gazpacho_andaluz.jpg/640px-Gazpacho_andaluz.jpg",
                  isFav=False
              ),
              RecipeResponse(
                  name="Paella valenciana",
                  category="Principal",
                  servings=4,
                  ingredients="400g arroz, 500g pollo, 200g judías verdes, 1 tomate, azafrán, pimentón, aceite, sal",
                  prep_time=60,
                  description="El plato más famoso de la cocina española con arroz y pollo.",
                  image="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Paella_valenciana_original.jpg/640px-Paella_valenciana_original.jpg",
                  isFav=False
              ),
              RecipeResponse(
                  name="Croquetas de jamón",
                  category="Aperitivo",
                  servings=4,
                  ingredients="100g jamón serrano, 500ml leche, 50g mantequilla, 100g harina, pan rallado, huevo,aceite",
                  prep_time=45,
                  description="Croquetas cremosas de jamón serrano, crujientes por fuera y suaves por dentro.",
                image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Croquetas_de_jamon.jpg/640px-Croquetas_de_jamon.jpg",
                isFav=False
              ),
              RecipeResponse(
                  name="Churros con chocolate",
                  category="Postre",
                  servings=2,
                  ingredients="200g harina, 250ml agua, sal, aceite para freír, 200g chocolate negro, 200ml leche",
                  prep_time=20,
                  description="Churros crujientes acompañados de espeso chocolate caliente para mojar.",
                  image="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Churros_fritos.jpg/640px-Churros_fritos.jpg",
                  isFav=False
              ),
          ]
          for recipe in recipes:
              session.add(recipe)
          session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    seed_recipes()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def root():
    return {"message": "Welcome to Maui's Recipe API!"}


@app.get("/recipes") 
def get_recipes(category: str | None = None):
    with Session(engine) as session:
        query = select(RecipeResponse)
        if category:
            query = query.where(RecipeResponse.category == category)
        recipes = session.exec(query).all() 
    return recipes


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    with Session(engine) as session:
        recipe = session.get(RecipeResponse, recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe.last_visited_at = datetime.now()
        session.add(recipe)
        session.commit()
        session.refresh(recipe)
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


