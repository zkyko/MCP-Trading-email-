#!/usr/bin/env python3
"""
Test script to verify the email fix
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_email_config():
    """Test if email configuration is available"""
    print("=== Email Configuration Test ===")
    
    required_vars = ["SENDGRID_API_KEY", "FROM_EMAIL", "TO_EMAIL"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * 20}")  # Hide sensitive data
        else:
            print(f"✗ {var}: Not set")
            missing.append(var)
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All email environment variables are set")
        return True

def test_import_email_utils():
    """Test if email utilities can be imported"""
    print("\n=== Email Utils Import Test ===")
    
    try:
        # Test import
        sys.path.append(os.path.join(os.path.dirname(__file__), 'email_utils'))
        from sendgrid_client import send_trade_email
        print("✅ Successfully imported send_trade_email")
        
        from trade_summary import summarize_trade
        print("✅ Successfully imported summarize_trade")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_send_simple_email():
    """Test sending a simple email"""
    print("\n=== Simple Email Test ===")
    
    if not test_email_config():
        print("❌ Cannot test email - configuration missing")
        return False
    
    try:
        # Import email function
        sys.path.append(os.path.join(os.path.dirname(__file__), 'email_utils'))
        from sendgrid_client import send_trade_email
        
        # Create test trade data
        test_trade = {
            'trade_id': 'TEST-FIX-001',
            'ticker': 'TESTCOIN',
            'direction': 'long',
            'entry_price': 100.0,
            'exit_price': 105.0,
            'pnl': '+5.00 USD',
            'pnl_amount': 5.0,
            'date_time': '2025-07-09 12:00:00',
            'timeframe': '5m',
            'reason_or_annotations': 'Test trade to verify email fix'
        }
        
        test_summary = """
EMAIL FIX TEST SUMMARY

This is a test email to verify that the SendGrid email fix is working correctly.

The fix includes:
- Fallback from dynamic template to regular HTML email
- Proper error handling for template ID issues
- ASCII-only content to prevent encoding errors
- Better subject line formatting

If you received this email, the fix is working!
        """.strip()
        
        print("📧 Sending test email...")
        result = send_trade_email(test_trade, test_summary)
        
        if result.get("success"):
            print(f"✅ Email sent successfully!")
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Template ID: {result.get('template_id', 'N/A')}")
            return True
        else:
            print(f"❌ Email failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during email test: {str(e)}")
        return False

def test_dynamic_emailer():
    """Test the dynamic trading emailer"""
    print("\n=== Dynamic Emailer Test ===")
    
    try:
        from dynamic_trading_emailer import DynamicTradingEmailer
        
        emailer = DynamicTradingEmailer()
        
        if not emailer.is_configured():
            print("❌ Dynamic emailer not configured")
            return False
        
        # Test with fake trade data
        test_trade = {
            'trade_id': 'DYNAMIC-TEST-001',
            'ticker': 'BTCUSD',
            'direction': 'short',
            'entry_price': 50000.0,
            'exit_price': 49500.0,
            'pnl': '+500.00 USD',
            'pnl_amount': 500.0,
            'date_time': '2025-07-09 12:05:00'
        }
        
        test_summary = "Dynamic emailer test - this should work with the new fix!"
        
        print("📧 Testing dynamic emailer...")
        result = emailer.send_email_with_template(test_trade, test_summary)
        
        if result.get("success"):
            print(f"✅ Dynamic emailer sent successfully!")
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Template ID: {result.get('template_id', 'N/A')}")
            return True
        else:
            print(f"❌ Dynamic emailer failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during dynamic emailer test: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🔧 Email Fix Verification Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_email_config),
        ("Import Utils", test_import_email_utils),
        ("Simple Email", test_send_simple_email),
        ("Dynamic Emailer", test_dynamic_emailer)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Email fix is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
