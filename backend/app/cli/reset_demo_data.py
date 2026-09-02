import asyncio
import sys
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.services.admin.data_reset import reset_demo_and_lead_data

async def main():
    print("==================================================")
    print(" LEADFORGE — DEMO DATA RESET UTILITY")
    print("==================================================")
    print("Purging all demo companies, leads, audits, and discovery jobs...")
    
    await init_db()
    async with AsyncSessionLocal() as session:
        result = await reset_demo_and_lead_data(session)
        print("\nReset status:", result["status"])
        print(result["message"])
        print("\nDeleted record summary:")
        for table, count in result["records_deleted"].items():
            if count > 0:
                print(f" - {table}: {count} records deleted")
    print("\nDatabase is now completely clean and ready for real global lead discovery.")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
