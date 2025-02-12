from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient("mongodb://localhost:27017") 
db = client["test_database"]
 
async def test_connection():
    try:  
        await db.command("ping")  # Test the connection 
        print("MongoDB connection is successful!") 
    except Exception as e:   
        print(f"MongoDB connection failed: {e}")  

import asyncio 
asyncio.run(test_connection())
