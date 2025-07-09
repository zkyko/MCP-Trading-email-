#!/usr/bin/env python3
"""
Test script to verify the email functionality in the web API server.
"""

import requests
import json
import os
from time import sleep

# API configuration
API_BASE = "http://localhost:8001"
TEST_IMAGE_PATH = "test_trade_image.png"  # You'll need to provide a test image

def test_extract_trade_with_email():
    """Test the /extract-trade endpoint with email enabled"""
    print("🧪 Testing /extract-trade endpoint with email...")
    
    # Test data
    payload = {
        "image_path": TEST_IMAGE_PATH,
        "send_email": True
    }
    
    try:
        response = requests.post(f"{API_BASE}/extract-trade", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(json.dumps(data, indent=2))
            
            # Check email status
            email_status = data.get("data", {}).get("email_status", "Not found")
            auto_email_status = data.get("data", {}).get("auto_email_status", "Not found")
            
            print(f"\n📧 Email Status: {email_status}")
            print(f"🔔 Auto-Email Status: {auto_email_status}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def test_extract_trade_upload_with_email():
    """Test the /extract-trade-upload endpoint with email enabled"""
    print("\n🧪 Testing /extract-trade-upload endpoint with email...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return None
    
    try:
        # Upload file with email enabled
        with open(TEST_IMAGE_PATH, "rb") as f:
            files = {"file": f}
            params = {"send_email": True}
            
            response = requests.post(f"{API_BASE}/extract-trade-upload", files=files, params=params)
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Response received:")
            print(json.dumps(data, indent=2))
            
            # Check email status
            email_status = data.get("data", {}).get("email_status", "Not found")
            auto_email_status = data.get("data", {}).get("auto_email_status", "Not found")
            
            print(f"\n📧 Email Status: {email_status}")
            print(f"🔔 Auto-Email Status: {auto_email_status}")
            
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def check_api_health():
    """Check if the API is running"""
    print("🏥 Checking API health...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not reachable: {str(e)}")
        return False

def test_without_email():
    """Test the endpoint without email to compare"""
    print("\n🧪 Testing without email for comparison...")
    
    payload = {
        "image_path": TEST_IMAGE_PATH,
        "send_email": False
    }
    
    try:
        response = requests.post(f"{API_BASE}/extract-trade", json=payload)
        if response.status_code == 200:
            data = response.json()
            email_status = data.get("data", {}).get("email_status", "Not found")
            print(f"📧 Email Status (disabled): {email_status}")
            return data
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting Email API Tests")
    print("=" * 50)
    
    # Check if API is running
    if not check_api_health():
        print("\n❌ API is not running. Please start the web API server first:")
        print("python web_api_server.py")
        return
    
    print(f"\n📁 Looking for test image: {TEST_IMAGE_PATH}")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"⚠️  Test image not found. Please provide a test image at: {TEST_IMAGE_PATH}")
        print("You can use any trading screenshot image.")
        
        # Try to find an image in uploads directory
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            images = [f for f in os.listdir(uploads_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if images:
                global TEST_IMAGE_PATH
                TEST_IMAGE_PATH = os.path.join(uploads_dir, images[0])
                print(f"✅ Using existing image: {TEST_IMAGE_PATH}")
            else:
                print("❌ No images found in uploads directory")
                return
        else:
            print("❌ No uploads directory found")
            return
    
    # Run tests
    print("\n" + "=" * 50)
    
    # Test 1: Extract trade without email
    result1 = test_without_email()
    
    # Test 2: Extract trade with email
    result2 = test_extract_trade_with_email()
    
    # Test 3: Upload with email
    result3 = test_extract_trade_upload_with_email()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"✅ Without email: {'PASS' if result1 else 'FAIL'}")
    print(f"✅ Extract with email: {'PASS' if result2 else 'FAIL'}")
    print(f"✅ Upload with email: {'PASS' if result3 else 'FAIL'}")
    
    if result2:
        print("\n🔍 Email functionality analysis:")
        data = result2.get("data", {})
        if data.get("email_sent"):
            print("✅ Email sending is working!")
        else:
            print(f"ℹ️  Email not sent: {data.get('email_status', 'Unknown')}")
            
        if data.get("auto_email_sent"):
            print("✅ Auto-email is working!")
        else:
            print(f"ℹ️  Auto-email not sent: {data.get('auto_email_status', 'Unknown')}")

if __name__ == "__main__":
    main()
