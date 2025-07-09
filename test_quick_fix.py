#!/usr/bin/env python3
"""
Quick test to verify the email fix is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_fixed_email():
    """Test the fixed email functionality"""
    print("🔧 Testing FIXED Email System")
    print("=" * 50)
    
    # Test environment variables
    required_vars = ["SENDGRID_API_KEY", "FROM_EMAIL", "TO_EMAIL"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Missing")
            missing.append(var)
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("\n📧 Testing Email Functions...")
    
    # Test 1: sendgrid_client
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'email_utils'))
        from sendgrid_client import send_test_email
        
        print("1️⃣ Testing sendgrid_client...")
        result1 = send_test_email()
        
        if result1.get("success"):
            print(f"   ✅ sendgrid_client: SUCCESS ({result1.get('status_code')})")
        else:
            print(f"   ❌ sendgrid_client: FAILED - {result1.get('error')}")
            
    except Exception as e:
        print(f"   ❌ sendgrid_client: ERROR - {str(e)}")
        
    # Test 2: dynamic_trading_emailer  
    try:
        from dynamic_trading_emailer import DynamicTradingEmailer
        
        print("2️⃣ Testing dynamic_trading_emailer...")
        emailer = DynamicTradingEmailer()
        
        # Create test trade
        test_trade = {
            'trade_id': 'SYSTEM-TEST-001',
            'ticker': 'TESTUSD',
            'direction': 'long',
            'entry_price': 100.0,
            'exit_price': 105.0,
            'pnl': '+5.00 USD',
            'pnl_amount': 5.0,
            'date_time': '2025-07-09 14:00:00',
            'timeframe': '5m'
        }
        
        result2 = emailer.send_email_with_template(test_trade, "SYSTEM TEST - Fixed email system working!")
        
        if result2.get("success"):
            print(f"   ✅ dynamic_trading_emailer: SUCCESS ({result2.get('status_code')})")
        else:
            print(f"   ❌ dynamic_trading_emailer: FAILED - {result2.get('error')}")
            
    except Exception as e:
        print(f"   ❌ dynamic_trading_emailer: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 If you received test emails, the fix is working!")
    print("📤 Try uploading a trade image with email enabled now.")
    
    return True

if __name__ == "__main__":
    test_fixed_email()
