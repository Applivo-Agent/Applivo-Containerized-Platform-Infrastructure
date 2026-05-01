import asyncio
import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from app.services.invoice_service import invoice_service

async def test_invoice_generation():
    print("🚀 Starting test invoice generation...")
    
    # Mock data
    data = {
        "payment_id": "pay_test_12345",
        "order_id": "order_test_98765",
        "full_name": "Sudharsan Test",
        "email": "ss0856@srmist.edu.in",
        "user_id": "user_trial_001",
        "amount": 499.00,
        "plan_name": "pro"
    }
    
    try:
        pdf_path = await invoice_service.generate_invoice(**data)
        
        if os.path.exists(pdf_path):
            print(f"✅ Success! Invoice generated at: {pdf_path}")
            print(f"📁 Size: {os.path.getsize(pdf_path)} bytes")
        else:
            print(f"❌ Error: PDF file was not created at {pdf_path}")
            
    except Exception as e:
        print(f"❌ Exception during generation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_invoice_generation())
