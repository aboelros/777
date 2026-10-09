import asyncio
from app.core.database import engine
async def main():
    print("DIALECT:", engine.dialect.name)
asyncio.run(main())
