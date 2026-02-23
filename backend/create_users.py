import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'eventpay_db')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if admin exists
    existing_admin = await db.users.find_one({"email": "admin@eventpay.com"})
    
    if not existing_admin:
        admin_user = {
            "email": "admin@eventpay.com",
            "password_hash": pwd_context.hash("admin123"),
            "name": "Administrador",
            "phone": "+55 11 99999-9999",
            "role": "admin",
            "credits": 100.0,
            "created_at": "2025-01-01T00:00:00"
        }
        await db.users.insert_one(admin_user)
        print("✅ Admin criado com sucesso!")
        print("Email: admin@eventpay.com")
        print("Senha: admin123")
    else:
        print("ℹ️  Admin já existe")
    
    # Create a regular user
    existing_user = await db.users.find_one({"email": "user@eventpay.com"})
    if not existing_user:
        regular_user = {
            "email": "user@eventpay.com",
            "password_hash": pwd_context.hash("user123"),
            "name": "Usuário Teste",
            "phone": "+55 11 98888-8888",
            "role": "user",
            "credits": 50.0,
            "created_at": "2025-01-01T00:00:00"
        }
        await db.users.insert_one(regular_user)
        print("✅ Usuário teste criado!")
        print("Email: user@eventpay.com")
        print("Senha: user123")
    else:
        print("ℹ️  Usuário teste já existe")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_admin())
