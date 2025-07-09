"""
Quick test of the final email integration
"""
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and test
from final_email_integration import send_nq1_trade_email, TradingEmailer

print("Testing Final Email Integration")
print("=" * 40)

# Test 1: Check configuration
print("1. Checking email configuration...")
emailer = TradingEmailer()
print(f"   Email configured: {emailer.is_configured()}")
if not emailer.is_configured():
    print("   Error: Email not configured properly!")
    print("   Please check your .env file for SENDGRID_API_KEY, FROM_EMAIL, TO_EMAIL")
    sys.exit(1)

# Test 2: Send NQ1! trade email
print("\n2. Sending NQ1! trade email...")
result = send_nq1_trade_email()

if result.get("success"):
    print("   [SUCCESS] Email sent successfully!")
    print(f"   Status: {result.get('status_code')}")
    print(f"   Message: {result.get('message')}")
else:
    print("   [ERROR] Email failed!")
    print(f"   Error: {result.get('error')}")

print("\nTest complete!")
