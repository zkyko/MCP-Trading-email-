"""
Test the dynamic trading emailer with live data
"""
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from dynamic_trading_emailer import DynamicTradingEmailer, send_latest_trade_email, send_all_trades_email

print("Testing Dynamic Trading Emailer with Live Data")
print("=" * 60)

# Initialize emailer
emailer = DynamicTradingEmailer()

# Test 1: Check configuration
print("1. Checking email configuration...")
print(f"   Email configured: {emailer.is_configured()}")
if not emailer.is_configured():
    print("   Error: Email not configured properly!")
    sys.exit(1)

# Test 2: Check latest trade
print("\n2. Checking latest trade data...")
latest_trade = emailer.get_latest_trade()
if latest_trade:
    print(f"   Latest trade found: {latest_trade.get('ticker')} {latest_trade.get('direction')} - ${latest_trade.get('pnl_amount')}")
    print(f"   Trade ID: {latest_trade.get('trade_id')}")
    print(f"   Date: {latest_trade.get('date_time')}")
else:
    print("   No latest trade found!")

# Test 3: Check trading stats
print("\n3. Current trading statistics...")
stats = emailer.get_trading_stats()
print(f"   Total trades: {stats.get('total_trades')}")
print(f"   Win rate: {stats.get('win_rate')}%")
print(f"   Total P&L: ${stats.get('total_pnl')}")

# Test 4: Send latest trade email
print("\n4. Sending latest trade email...")
result = send_latest_trade_email()

if result.get("success"):
    print("   [SUCCESS] Latest trade email sent!")
    print(f"   Status: {result.get('status_code')}")
    print(f"   Message: {result.get('message')}")
else:
    print("   [ERROR] Latest trade email failed!")
    print(f"   Error: {result.get('error')}")

print("\nTest complete!")
print("\nAvailable commands for future use:")
print("  python dynamic_trading_emailer.py latest   # Send latest trade")
print("  python dynamic_trading_emailer.py all      # Send all trades summary")
print("  python dynamic_trading_emailer.py daily    # Send daily summary")
print("  python dynamic_trading_emailer.py weekly   # Send weekly summary")
