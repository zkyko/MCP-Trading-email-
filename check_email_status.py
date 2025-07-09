#!/usr/bin/env python3
"""
Quick Email Status Checker
Provides a quick overview of email functionality status
"""

import os
import sys
from datetime import datetime

def check_email_status():
    """Quick check of email functionality status"""
    print("📧 EMAIL FUNCTIONALITY STATUS CHECK")
    print("=" * 50)
    print(f"🕒 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if required directories exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    email_utils_dir = os.path.join(base_dir, "email_utils")
    debug_tools_dir = os.path.join(base_dir, "debug_tools")
    logs_dir = os.path.join(base_dir, "logs")
    
    print("📁 Directory Check:")
    print(f"   email_utils/: {'✅' if os.path.exists(email_utils_dir) else '❌'}")
    print(f"   debug_tools/: {'✅' if os.path.exists(debug_tools_dir) else '❌'}")
    print(f"   logs/: {'✅' if os.path.exists(logs_dir) else '❌'}")
    print()
    
    # Check key files
    key_files = {
        "email_utils/sendgrid_client.py": os.path.join(email_utils_dir, "sendgrid_client.py"),
        "email_utils/trade_summary.py": os.path.join(email_utils_dir, "trade_summary.py"),
        "debug_tools/email_debugger.py": os.path.join(debug_tools_dir, "email_debugger.py"),
        "test_email.py": os.path.join(base_dir, "test_email.py"),
    }
    
    print("📄 File Check:")
    for name, path in key_files.items():
        print(f"   {name}: {'✅' if os.path.exists(path) else '❌'}")
    print()
    
    # Check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        "SENDGRID_API_KEY": os.getenv("SENDGRID_API_KEY"),
        "FROM_EMAIL": os.getenv("FROM_EMAIL"),
        "TO_EMAIL": os.getenv("TO_EMAIL"),
    }
    
    print("🔧 Environment Variables:")
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        display_value = f"({value[:10]}...)" if value and len(value) > 10 else "(not set)"
        print(f"   {var}: {status} {display_value}")
    
    config_complete = all(env_vars.values())
    print(f"\n   Configuration Complete: {'✅' if config_complete else '❌'}")
    print()
    
    # Check if email functionality can be imported
    try:
        sys.path.append(email_utils_dir)
        sys.path.append(debug_tools_dir)
        from sendgrid_client import send_test_email
        from email_debugger import email_debugger
        import_status = "✅"
        import_error = None
    except ImportError as e:
        import_status = "❌"
        import_error = str(e)
    
    print("📦 Import Check:")
    print(f"   Email modules: {import_status}")
    if import_error:
        print(f"   Error: {import_error}")
    print()
    
    # Check recent email attempts if possible
    if import_status == "✅":
        try:
            stats = email_debugger.get_email_stats()
            print("📊 Recent Email Statistics:")
            print(f"   Total Attempts: {stats['total_attempts']}")
            print(f"   Successful: {stats['successful']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Success Rate: {stats['success_rate']}%")
            
            if stats['recent_attempts']:
                print(f"\n   Last Attempt:")
                last = stats['recent_attempts'][0]
                status = "✅" if last['success'] else "❌"
                print(f"   {status} {last['timestamp'][:19]} - Trade {last['trade_id']}")
            else:
                print("   No email attempts recorded yet")
                
        except Exception as e:
            print(f"   ❌ Error getting stats: {str(e)}")
    print()
    
    # Overall status
    overall_ready = (
        os.path.exists(email_utils_dir) and
        os.path.exists(debug_tools_dir) and
        config_complete and
        import_status == "✅"
    )
    
    print("🎯 Overall Status:")
    print(f"   Email Ready: {'✅ READY' if overall_ready else '❌ NOT READY'}")
    
    if not overall_ready:
        print("\n💡 Next Steps:")
        if not config_complete:
            print("   1. Complete email configuration in .env file")
        if import_status != "✅":
            print("   2. Install required packages: pip install sendgrid python-dotenv")
        print("   3. Run: python test_email.py config")
        print("   4. Run: python test_email.py test")
    else:
        print("\n🚀 Ready to send emails!")
        print("   Test with: python test_email.py test")
        print("   Use --send-email flag when processing trades")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    check_email_status()
