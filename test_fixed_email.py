"""
Test the fixed email system with ASCII-only content
"""
import sys
import os

# Add the email_utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'email_utils'))

from email_utils.sendgrid_client import send_test_email, send_latest_trade_email

def test_ascii_email():
    """Test the ASCII-only email functionality"""
    print("[TEST] Testing ASCII-only email system...")
    
    # Test 1: Basic test email
    print("[TEST] Sending basic test email...")
    result = send_test_email("This is a test of the ASCII-only email system. No emojis here!")
    print(f"[TEST] Basic test result: {result}")
    
    return result

def send_nq_trade_email():
    """Send email for the latest NQ1! trade"""
    print("[TEST] Sending NQ1! trade email...")
    
    # Your latest trade data
    latest_trade = {
        'trade_id': '1829480a',
        'ticker': 'NQ1!',
        'timeframe': 'Not specified',
        'entry_price': 22880.75,
        'exit_price': 22878.0,
        'direction': 'short',
        'pnl': '+2,220.00 usp',
        'pnl_amount': 2220.0,
        'date_time': '2025-07-08 22:12:32',
        'reason_or_annotations': 'Not specified',
        'image_source': 'NQ1!_2025-07-08_22-12-32_ef2ba.png',
        'logged_at': '2025-07-08T22:25:55.572680',
        'ocr_confidence': '78.9%'
    }
    
    result = send_latest_trade_email(latest_trade)
    print(f"[TEST] NQ1! trade email result: {result}")
    
    return result

if __name__ == "__main__":
    print("[MAIN] Starting email tests...")
    
    # First test basic functionality
    test_result = test_ascii_email()
    
    if test_result.get("success"):
        print("[SUCCESS] Basic email test passed! Sending trade email...")
        trade_result = send_nq_trade_email()
        
        if trade_result.get("success"):
            print("[SUCCESS] Trade email sent successfully!")
        else:
            print(f"[ERROR] Trade email failed: {trade_result.get('error')}")
    else:
        print(f"[ERROR] Basic email test failed: {test_result.get('error')}")
        print("[SKIP] Skipping trade email due to basic test failure")
