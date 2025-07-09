#!/usr/bin/env python3
"""
Email Test Script
Test and debug email functionality for the trading system.
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Make sure we load .env variables

# Add project paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_utils'))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_tools'))

# Try to import email modules
try:
    from email_utils.sendgrid_client import send_test_email, send_trade_email
    from email_utils.trade_summary import summarize_trade
    from debug_tools.email_debugger import email_debugger
    EMAIL_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importing email modules: {e}")
    EMAIL_AVAILABLE = False

def test_email_configuration():
    """Test email configuration and display status"""
    print("\n" + "="*60)
    print("🧪 EMAIL CONFIGURATION TEST")
    print("="*60)
    
    if not EMAIL_AVAILABLE:
        print("❌ Email modules not available")
        return False
    
    config_result = email_debugger.test_email_configuration()
    
    print(f"\n🔧 Configuration Check:")
    config = config_result['config_check']
    print(f"   SendGrid API Key: {'✅' if config['sendgrid_api_key'] else '❌'}")
    print(f"   From Email: {'✅' if config['from_email'] else '❌'}")
    print(f"   To Email: {'✅' if config['to_email'] else '❌'}")
    print(f"   Complete: {'✅' if config['config_complete'] else '❌'}")
    
    if config_result['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in config_result['recommendations']:
            print(f"   • {rec}")
    
    return config['config_complete']

def send_test_email_now():
    """Send a basic test email"""
    print("\n" + "="*60)
    print("📧 SENDING TEST EMAIL")
    print("="*60)
    
    if not EMAIL_AVAILABLE:
        print("❌ Email functionality not available")
        return False
    
    try:
        print("📤 Sending test email...")
        result = send_test_email("🧪 This is a test email from your trading system!")
        
        if result.get('success'):
            print(f"✅ Test email sent successfully!")
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Test email failed!")
            print(f"   Error: {result.get('error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Exception during test email: {str(e)}")
        return False

def send_sample_trade_email():
    """Send a sample trade email"""
    print("\n" + "="*60)
    print("📊 SENDING SAMPLE TRADE EMAIL")
    print("="*60)

    if not EMAIL_AVAILABLE:
        print("❌ Email functionality not available")
        return False

    # Log environment variables
    print("🔍 ENV CHECK")
    print(f"   SENDGRID_API_KEY: {'✅' if os.getenv('SENDGRID_API_KEY') else '❌ MISSING'}")
    print(f"   FROM_EMAIL: {os.getenv('FROM_EMAIL')}")
    print(f"   TO_EMAIL: {os.getenv('TO_EMAIL')}")

    sample_trade = {
        'trade_id': 'SAMPLE-001',
        'ticker': 'BTCUSD',
        'symbol': 'BTCUSD',
        'timeframe': '5m',
        'entry_price': 45000.00,
        'exit_price': 45500.00,
        'direction': 'long',
        'pnl': '+$500.00',
        'pnl_amount': 500.00,
        'date_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reason_or_annotations': 'Sample trade for testing email functionality',
        'image_source': 'sample_chart.png',
        'logged_at': datetime.now().isoformat(),
        'ocr_confidence': '95.5%'
    }

    try:
        print("🤖 Generating AI summary...")
        summary = summarize_trade(sample_trade)
        print("📤 Sending trade email...")
        result = send_trade_email(sample_trade, summary)

        if result.get('success'):
            print("✅ Sample trade email sent successfully!")
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Trade ID: {result.get('trade_id')}")
            print(f"   Message: {result.get('message')}")
        else:
            print("❌ Sample trade email failed!")
            print(f"   Error: {result.get('error')}")

        return result.get('success', False)

    except Exception as e:
        print(f"❌ Exception during sample trade email: {str(e)}")
        return False

def show_email_statistics():
    """Display email sending statistics"""
    print("\n" + "="*60)
    print("📊 EMAIL STATISTICS")
    print("="*60)
    
    if not EMAIL_AVAILABLE:
        print("❌ Email functionality not available")
        return

    try:
        stats = email_debugger.get_email_stats()

        print("\n📈 Summary:")
        print(f"   Total Attempts: {stats['total_attempts']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success Rate: {stats['success_rate']}%")

        if stats['recent_attempts']:
            print("\n📝 Recent Attempts (last 5):")
            for attempt in stats['recent_attempts'][:5]:
                status = "✅" if attempt['success'] else "❌"
                timestamp = attempt['timestamp'][:19]
                print(f"   {status} {timestamp} - Trade {attempt['trade_id']}")
                if not attempt['success'] and attempt.get('error_message'):
                    print(f"      Error: {attempt['error_message']}")
        else:
            print("\n📝 No email attempts recorded yet")

    except Exception as e:
        print(f"❌ Error retrieving statistics: {str(e)}")

def print_usage():
    """Print usage information"""
    print("\n📖 Usage:")
    print("   python test_email.py <command>")
    print("\n🔧 Commands:")
    print("   config  - Test email configuration")
    print("   test    - Send a test email")
    print("   sample  - Send a sample trade email")
    print("   stats   - Show email statistics")
    print("   debug   - Show comprehensive debug info")
    print("   all     - Run all tests")
    print("\n💡 Examples:")
    print("   python test_email.py config")
    print("   python test_email.py test")
    print("   python test_email.py all")

def main():
    """Main command dispatcher"""
    print("🧪 EMAIL FUNCTIONALITY TEST SUITE")
    print("==" * 30)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        print(f"🚀 Running command: {command}")
        
        if command == "config":
            test_email_configuration()
        elif command == "test":
            if test_email_configuration():
                send_test_email_now()
            else:
                print("\n❌ Configuration incomplete. Fix configuration before testing.")
        elif command == "sample":
            if test_email_configuration():
                send_sample_trade_email()
            else:
                print("\n❌ Configuration incomplete. Fix configuration before testing.")
        elif command == "stats":
            show_email_statistics()
        elif command == "debug":
            email_debugger.print_debug_info()
        elif command == "all":
            config_ok = test_email_configuration()
            show_email_statistics()
            if config_ok:
                send_test_email_now()
                send_sample_trade_email()
            else:
                print("\n❌ Configuration incomplete. Skipping email tests.")
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
    else:
        print_usage()

if __name__ == "__main__":
    main()
