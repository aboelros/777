import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def check_schema():
    async with AsyncSessionLocal() as session:
        for table in ['api_logs', 'messages', 'orders', 'knowledge_base']:
            print(f"\n--- Columns in {table} ---")
            try:
                result = await session.execute(text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position;
                """))
                columns = result.fetchall()
                for col in columns:
                    print(f"{col[0]}: {col[1]}")
            except Exception as e:
                print(f"Error checking {table}: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
