"""
Test the direct email function
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from direct_email import send_direct_email

# Test the direct email function
trade_message = """Trade Alert: NQ1 Short Position - Profit $2220.00

Your latest trade on NQ1 (NASDAQ Futures) was successful:
Entry: $22880.75
Exit: $22878.00
Direction: Short
Profit: $2220.00
Date: July 8, 2025

This brings your total PnL to $3756.63 across 11 trades with a 72.7% win rate.

Excellent short trade that captured the downward move perfectly!"""

print("[TEST] Testing direct email function...")
result = send_direct_email(trade_message)
print(f"[RESULT] {result}")

if result.get("success"):
    print("[SUCCESS] Direct email sent successfully!")
else:
    print(f"[ERROR] Direct email failed: {result.get('error')}")
