from fastapi import FastAPI
from app.core.database import Base, engine
from app.auth import models as auth_models
from app.products import models as product_models
from app.cart import models as cart_models
from app.orders import models as order_models
from app.auth.routes import router as auth_router
from app.products.routes import router as admin_products_router 
from app.products.routes_public import router as public_product_router
from app.cart.routes import router as cart_router
from app.checkout.routes import router as checkout_router
from app.orders.rotues import router as orders_router
from app.cart.models import Cart

from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

app.include_router(auth_router)
#  Include admin routes
app.include_router(admin_products_router)  
# public product router
app.include_router(public_product_router)
# cart router
app.include_router(cart_router)
# checkout router
app.include_router(checkout_router)
# order router
app.include_router(orders_router)


# Create all tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "E-commerce API is running!"}
