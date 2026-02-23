from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from bson import ObjectId

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str]
    role: str
    credits: float

class EventCreate(BaseModel):
    name: str
    description: str
    date: str
    location: str
    image_base64: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    name: str
    description: str
    date: str
    location: str
    image_base64: Optional[str]
    status: str
    organizer_id: str
    created_at: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    image_base64: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    event_id: str
    name: str
    description: str
    price: float
    stock: int
    image_base64: Optional[str]
    available: bool

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    event_id: str
    items: List[OrderItem]
    use_credits: float = 0.0

class OrderResponse(BaseModel):
    id: str
    user_id: str
    event_id: str
    event_name: str
    items: List[OrderItem]
    subtotal: float
    platform_fee: float
    credits_used: float
    total: float
    organizer_amount: float
    payment_status: str
    qr_code: str
    status: str
    created_at: str

# AUTH ROUTES
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Create user
    user_dict = {
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "name": user_data.name,
        "phone": user_data.phone,
        "role": "user",
        "credits": 0.0,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)
    
    # Create token
    token = create_access_token({"sub": user_id, "email": user_data.email})
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "phone": user_data.phone,
            "role": "user",
            "credits": 0.0
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    logger.info(f"Login attempt for: {credentials.email}")
    logger.info(f"User found: {user is not None}")
    
    if not user:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    password_valid = verify_password(credentials.password, user["password_hash"])
    logger.info(f"Password valid: {password_valid}")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id, "email": user["email"]})
    
    return {
        "token": token,
        "user": {
            "id": user_id,
            "email": user["email"],
            "name": user["name"],
            "phone": user.get("phone"),
            "role": user["role"],
            "credits": user.get("credits", 0.0)
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "name": current_user["name"],
        "phone": current_user.get("phone"),
        "role": current_user["role"],
        "credits": current_user.get("credits", 0.0)
    }

# EVENT ROUTES
@api_router.get("/events")
async def get_events(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    
    events = await db.events.find(query).to_list(1000)
    return [{
        "id": str(event["_id"]),
        "name": event["name"],
        "description": event["description"],
        "date": event["date"],
        "location": event["location"],
        "image_base64": event.get("image_base64"),
        "status": event["status"],
        "organizer_id": event["organizer_id"],
        "created_at": event["created_at"]
    } for event in events]

@api_router.post("/events")
async def create_event(event_data: EventCreate, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar eventos")
    
    event_dict = {
        "name": event_data.name,
        "description": event_data.description,
        "date": event_data.date,
        "location": event_data.location,
        "image_base64": event_data.image_base64,
        "status": "active",
        "organizer_id": str(current_user["_id"]),
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.events.insert_one(event_dict)
    event_dict["id"] = str(result.inserted_id)
    return event_dict

@api_router.get("/events/{event_id}")
async def get_event(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return {
        "id": str(event["_id"]),
        "name": event["name"],
        "description": event["description"],
        "date": event["date"],
        "location": event["location"],
        "image_base64": event.get("image_base64"),
        "status": event["status"],
        "organizer_id": event["organizer_id"],
        "created_at": event["created_at"]
    }

@api_router.put("/events/{event_id}")
async def update_event(event_id: str, event_data: EventCreate, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar eventos")
    
    result = await db.events.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": event_data.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return {"message": "Evento atualizado com sucesso"}

@api_router.delete("/events/{event_id}")
async def delete_event(event_id: str, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar eventos")
    
    result = await db.events.delete_one({"_id": ObjectId(event_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    return {"message": "Evento deletado com sucesso"}

# PRODUCT ROUTES
@api_router.get("/events/{event_id}/products")
async def get_event_products(event_id: str):
    products = await db.products.find({"event_id": event_id}).to_list(1000)
    return [{
        "id": str(product["_id"]),
        "event_id": product["event_id"],
        "name": product["name"],
        "description": product["description"],
        "price": product["price"],
        "stock": product["stock"],
        "image_base64": product.get("image_base64"),
        "available": product["available"]
    } for product in products]

@api_router.post("/events/{event_id}/products")
async def create_product(event_id: str, product_data: ProductCreate, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar produtos")
    
    product_dict = {
        "event_id": event_id,
        "name": product_data.name,
        "description": product_data.description,
        "price": product_data.price,
        "stock": product_data.stock,
        "image_base64": product_data.image_base64,
        "available": True,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.products.insert_one(product_dict)
    product_dict["id"] = str(result.inserted_id)
    return product_dict

@api_router.put("/products/{product_id}")
async def update_product(product_id: str, product_data: ProductCreate, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar produtos")
    
    result = await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": product_data.dict()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {"message": "Produto atualizado com sucesso"}

@api_router.delete("/products/{product_id}")
async def delete_product(product_id: str, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem deletar produtos")
    
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    return {"message": "Produto deletado com sucesso"}

# ORDER ROUTES
@api_router.post("/orders")
async def create_order(order_data: OrderCreate, current_user = Depends(get_current_user)):
    # Get event
    event = await db.events.find_one({"_id": ObjectId(order_data.event_id)})
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    # Calculate totals
    subtotal = sum(item.unit_price * item.quantity for item in order_data.items)
    platform_fee = subtotal * 0.10  # 10% fee
    
    # Apply credits
    credits_used = min(order_data.use_credits, current_user.get("credits", 0.0))
    total = subtotal + platform_fee - credits_used
    
    if total < 0:
        total = 0
    
    organizer_amount = subtotal
    
    # Generate unique QR code
    qr_code = f"ORDER-{uuid.uuid4()}"
    
    # Create order
    order_dict = {
        "user_id": str(current_user["_id"]),
        "event_id": order_data.event_id,
        "event_name": event["name"],
        "items": [item.dict() for item in order_data.items],
        "subtotal": subtotal,
        "platform_fee": platform_fee,
        "credits_used": credits_used,
        "total": total,
        "organizer_amount": organizer_amount,
        "payment_status": "paid",  # Mockado como pago
        "qr_code": qr_code,
        "status": "pending",  # pending, validated, cancelled
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await db.orders.insert_one(order_dict)
    
    # Update user credits
    if credits_used > 0:
        await db.users.update_one(
            {"_id": current_user["_id"]},
            {"$inc": {"credits": -credits_used}}
        )
    
    # Update product stock
    for item in order_data.items:
        await db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )
    
    order_dict["id"] = str(result.inserted_id)
    return order_dict

@api_router.get("/orders")
async def get_my_orders(current_user = Depends(get_current_user)):
    orders = await db.orders.find({"user_id": str(current_user["_id"])}).to_list(1000)
    return [{
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "event_id": order["event_id"],
        "event_name": order["event_name"],
        "items": order["items"],
        "subtotal": order["subtotal"],
        "platform_fee": order["platform_fee"],
        "credits_used": order.get("credits_used", 0.0),
        "total": order["total"],
        "organizer_amount": order["organizer_amount"],
        "payment_status": order["payment_status"],
        "qr_code": order["qr_code"],
        "status": order["status"],
        "created_at": order["created_at"]
    } for order in orders]

@api_router.get("/orders/{order_id}")
async def get_order(order_id: str, current_user = Depends(get_current_user)):
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    # Check if user owns the order or is admin
    if order["user_id"] != str(current_user["_id"]) and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return {
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "event_id": order["event_id"],
        "event_name": order["event_name"],
        "items": order["items"],
        "subtotal": order["subtotal"],
        "platform_fee": order["platform_fee"],
        "credits_used": order.get("credits_used", 0.0),
        "total": order["total"],
        "organizer_amount": order["organizer_amount"],
        "payment_status": order["payment_status"],
        "qr_code": order["qr_code"],
        "status": order["status"],
        "created_at": order["created_at"]
    }

@api_router.post("/orders/{order_id}/validate")
async def validate_order(order_id: str, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem validar pedidos")
    
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    if order["status"] == "validated":
        raise HTTPException(status_code=400, detail="Pedido já foi validado")
    
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": "validated", "validated_at": datetime.utcnow().isoformat()}}
    )
    
    return {"message": "Pedido validado com sucesso"}

@api_router.post("/orders/validate-qr")
async def validate_qr_code(qr_code: str, current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem validar QR codes")
    
    order = await db.orders.find_one({"qr_code": qr_code})
    if not order:
        raise HTTPException(status_code=404, detail="QR Code inválido")
    
    if order["status"] == "validated":
        return {
            "message": "QR Code já foi validado anteriormente",
            "order": {
                "id": str(order["_id"]),
                "event_name": order["event_name"],
                "total": order["total"],
                "status": order["status"],
                "validated_at": order.get("validated_at")
            }
        }
    
    await db.orders.update_one(
        {"_id": order["_id"]},
        {"$set": {"status": "validated", "validated_at": datetime.utcnow().isoformat()}}
    )
    
    return {
        "message": "Pedido validado com sucesso!",
        "order": {
            "id": str(order["_id"]),
            "event_name": order["event_name"],
            "items": order["items"],
            "total": order["total"],
            "status": "validated"
        }
    }

# CREDITS ROUTES
@api_router.get("/credits/balance")
async def get_credits_balance(current_user = Depends(get_current_user)):
    return {"credits": current_user.get("credits", 0.0)}

@api_router.post("/credits/add")
async def add_credits(amount: float, current_user = Depends(get_current_user)):
    # This would be called after an event ends to convert unused balance
    await db.users.update_one(
        {"_id": current_user["_id"]},
        {"$inc": {"credits": amount}}
    )
    
    # Log credit transaction
    await db.credit_transactions.insert_one({
        "user_id": str(current_user["_id"]),
        "amount": amount,
        "type": "conversion",
        "created_at": datetime.utcnow().isoformat()
    })
    
    return {"message": "Créditos adicionados com sucesso", "new_balance": current_user.get("credits", 0.0) + amount}

# ADMIN ROUTES
@api_router.get("/admin/orders")
async def get_all_orders(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    orders = await db.orders.find().to_list(1000)
    return [{
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "event_id": order["event_id"],
        "event_name": order["event_name"],
        "items": order["items"],
        "subtotal": order["subtotal"],
        "platform_fee": order["platform_fee"],
        "total": order["total"],
        "payment_status": order["payment_status"],
        "qr_code": order["qr_code"],
        "status": order["status"],
        "created_at": order["created_at"]
    } for order in orders]

@api_router.get("/admin/reports")
async def get_reports(current_user = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # Calculate totals
    orders = await db.orders.find({"payment_status": "paid"}).to_list(10000)
    
    total_sales = sum(order["total"] for order in orders)
    platform_fees = sum(order["platform_fee"] for order in orders)
    organizer_amount = sum(order["organizer_amount"] for order in orders)
    
    return {
        "total_orders": len(orders),
        "total_sales": total_sales,
        "platform_fees": platform_fees,
        "organizer_amount": organizer_amount
    }

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
