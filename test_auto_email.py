"""
Test the auto-email functionality integrated into enhanced_extract_trade.py
"""
import os
import sys
import json

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
sys.path.insert(0, tools_dir)

from enhanced_extract_trade import process_single_image

print("Testing Auto-Email Integration")
print("=" * 50)

# Find a sample image to test with (or create a dummy test)
uploads_dir = "uploads"
if os.path.exists(uploads_dir):
    image_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if image_files:
        test_image = os.path.join(uploads_dir, image_files[0])
        print(f"Found test image: {test_image}")
        
        print("\nTesting trade processing with auto-email enabled...")
        print("This will:")
        print("1. Process the image with OCR")
        print("2. Analyze with DeepSeek")
        print("3. Save trade data")
        print("4. Automatically send email alert")
        
        try:
            # Process image with email enabled
            result = process_single_image(test_image, save_mode="both", send_email=True)
            
            print("\nResults:")
            print(f"Trade processed: {result.get('trade_id')}")
            print(f"Ticker: {result.get('ticker')}")
            print(f"P&L: {result.get('pnl_amount')}")
            print(f"Auto-email sent: {result.get('auto_email_sent')}")
            print(f"Auto-email status: {result.get('auto_email_status')}")
            
            if result.get('auto_email_sent'):
                print("\n[SUCCESS] Auto-email sent successfully!")
            else:
                print(f"\n[INFO] Auto-email not sent: {result.get('auto_email_status')}")
                
        except Exception as e:
            print(f"\n[ERROR] Test failed: {str(e)}")
    else:
        print("No image files found in uploads directory")
else:
    print("uploads directory not found")

print("\nNext steps:")
print("1. Upload a trading chart image to the uploads/ directory")
print("2. Run: python enhanced_extract_trade.py path/to/image.png --send-email")
print("3. The system will automatically send an email after processing")
