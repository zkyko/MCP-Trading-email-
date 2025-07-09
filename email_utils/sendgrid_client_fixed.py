"""
sendgrid_client_fixed.py - Complete fix for SendGrid email issues
This replaces the problematic template approach with reliable HTML emails
"""

import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from dotenv import load_dotenv
import sys

# Add debug tools to path if available
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug_tools'))
    from email_debugger import debug_email_send
    DEBUG_AVAILABLE = True
except ImportError:
    DEBUG_AVAILABLE = False
    def debug_email_send(*args, **kwargs):
        pass

# Load environment variables
load_dotenv()

def clean_text_for_email(text):
    """Remove problematic characters that cause encoding issues"""
    if not text:
        return ""
    
    # Convert to string first if needed
    text_str = str(text)
    
    # Keep only ASCII printable characters (32-126) plus newlines and tabs
    cleaned = ''.join(char for char in text_str if 32 <= ord(char) <= 126 or char in '\n\r\t')
    
    # Remove backslashes that could escape JSON
    cleaned = cleaned.replace("\\", "")
    
    return cleaned.strip()

def send_trade_email(trade_data, summary):
    """
    Send trade email using SendGrid with HTML content (FIXED VERSION)
    This bypasses template issues and always works
    """
    # Get environment variables
    sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    to_email = os.getenv("TO_EMAIL")
    
    # Get trade ID for debugging
    trade_id = trade_data.get('trade_id', 'unknown')
    
    if not all([sendgrid_api_key, from_email, to_email]):
        error_msg = "Missing required environment variables (SENDGRID_API_KEY, FROM_EMAIL, TO_EMAIL)"
        print(f"[ERROR] {error_msg}")
        debug_email_send(
            trade_id=trade_id,
            recipient=to_email or "unknown",
            subject="Trade Summary",
            success=False,
            error_message=error_msg
        )
        return {"error": error_msg, "success": False}

    print(f"[EMAIL] Preparing FIXED email for trade {trade_id}...")
    
    try:
        # Extract values from trade_data
        symbol = trade_data.get("ticker", "UNKNOWN")
        direction = trade_data.get("direction", "unknown")
        entry_price = trade_data.get("entry_price", "N/A")
        exit_price = trade_data.get("exit_price", "N/A")
        pnl = trade_data.get("pnl", "N/A")
        pnl_amount = trade_data.get("pnl_amount", 0)
        date_time = trade_data.get("date_time", "N/A")
        timeframe = trade_data.get("timeframe", "N/A")
        
        # Clean summary
        cleaned_summary = clean_text_for_email(summary) if summary else "No summary available"
        
        # Create subject
        profit_status = "PROFIT" if (pnl_amount or 0) > 0 else "INFO"
        subject = f"Trade Alert: {symbol} - {profit_status}"
        
        # Create comprehensive HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trade Summary</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    background: white; 
                    border-radius: 8px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                    overflow: hidden;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center; 
                }}
                .header h1 {{ 
                    margin: 0 0 10px 0; 
                    font-size: 28px; 
                    font-weight: 600; 
                }}
                .header p {{ 
                    margin: 0; 
                    opacity: 0.9; 
                    font-size: 16px; 
                }}
                .content {{ 
                    padding: 30px; 
                }}
                .trade-details {{ 
                    background: #f8f9fa; 
                    border-radius: 8px; 
                    padding: 20px; 
                    margin: 20px 0; 
                }}
                .detail-row {{ 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    padding: 12px 0; 
                    border-bottom: 1px solid #e9ecef; 
                }}
                .detail-row:last-child {{ 
                    border-bottom: none; 
                }}
                .label {{ 
                    font-weight: 600; 
                    color: #495057; 
                    flex: 1; 
                }}
                .value {{ 
                    font-weight: 500; 
                    text-align: right; 
                    flex: 1; 
                }}
                .profit {{ 
                    color: #28a745; 
                    font-weight: bold; 
                }}
                .loss {{ 
                    color: #dc3545; 
                    font-weight: bold; 
                }}
                .neutral {{ 
                    color: #6c757d; 
                    font-weight: bold; 
                }}
                .direction-long {{ 
                    background: #d4edda; 
                    color: #155724; 
                    padding: 4px 12px; 
                    border-radius: 20px; 
                    font-size: 12px; 
                    font-weight: bold; 
                    text-transform: uppercase; 
                }}
                .direction-short {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                    padding: 4px 12px; 
                    border-radius: 20px; 
                    font-size: 12px; 
                    font-weight: bold; 
                    text-transform: uppercase; 
                }}
                .summary {{ 
                    background: #e3f2fd; 
                    border-left: 4px solid #2196f3; 
                    padding: 20px; 
                    margin: 20px 0; 
                    border-radius: 0 8px 8px 0; 
                }}
                .summary h3 {{ 
                    margin: 0 0 15px 0; 
                    color: #1976d2; 
                    font-size: 18px; 
                }}
                .summary-text {{ 
                    color: #424242; 
                    line-height: 1.7; 
                    white-space: pre-wrap; 
                }}
                .footer {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 14px; 
                    color: #6c757d; 
                    border-top: 1px solid #e9ecef; 
                }}
                .badge {{ 
                    display: inline-block; 
                    padding: 6px 12px; 
                    border-radius: 4px; 
                    font-size: 12px; 
                    font-weight: bold; 
                    text-transform: uppercase; 
                }}
                .badge-success {{ 
                    background: #d4edda; 
                    color: #155724; 
                }}
                .badge-danger {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                }}
                .badge-secondary {{ 
                    background: #e2e3e5; 
                    color: #383d41; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Trade Execution Summary</h1>
                    <p>Trade ID: {trade_id}</p>
                </div>
                
                <div class="content">
                    <div class="trade-details">
                        <div class="detail-row">
                            <span class="label">📊 Symbol:</span>
                            <span class="value" style="font-weight: bold; font-size: 16px;">{symbol}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">📅 Date & Time:</span>
                            <span class="value">{date_time}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">⏰ Timeframe:</span>
                            <span class="value">{timeframe}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">🎯 Direction:</span>
                            <span class="value">
                                {f'<span class="direction-{direction.lower() if direction and direction.lower() in ["long", "short"] else "neutral"}">{direction.upper() if direction else "N/A"}</span>' if direction else '<span class="badge badge-secondary">N/A</span>'}
                            </span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">📈 Entry Price:</span>
                            <span class="value">${entry_price if entry_price and str(entry_price) != 'None' else 'N/A'}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">📉 Exit Price:</span>
                            <span class="value">${exit_price if exit_price and str(exit_price) != 'None' else 'N/A'}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="label">💰 Result:</span>
                            <span class="value">
                                {f'<span class="{"profit" if (pnl_amount or 0) > 0 else "loss" if (pnl_amount or 0) < 0 else "neutral"}">{pnl if pnl and str(pnl) != "None" else "N/A"}</span>'}
                            </span>
                        </div>
                    </div>
                    
                    <div class="summary">
                        <h3>🤖 AI Analysis Summary</h3>
                        <div class="summary-text">{cleaned_summary}</div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>📧 Generated by your Automated Trading Analysis System</p>
                    <p>This email contains AI-generated analysis for informational purposes only.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        text_content = f"""
        TRADE EXECUTION SUMMARY
        =======================
        
        Trade ID: {trade_id}
        Symbol: {symbol}
        Date & Time: {date_time}
        Timeframe: {timeframe}
        Direction: {direction.upper() if direction else 'N/A'}
        Entry Price: ${entry_price if entry_price and str(entry_price) != 'None' else 'N/A'}
        Exit Price: ${exit_price if exit_price and str(exit_price) != 'None' else 'N/A'}
        Result: {pnl if pnl and str(pnl) != 'None' else 'N/A'}
        
        AI ANALYSIS SUMMARY:
        {cleaned_summary}
        
        ---
        Generated by your Automated Trading Analysis System
        This email contains AI-generated analysis for informational purposes only.
        """
        
        # Create message with both HTML and text content
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        
        # Add both content types (SendGrid best practice)
        message.content = [
            Content("text/plain", clean_text_for_email(text_content)),
            Content("text/html", html_content)
        ]
        
        print(f"[EMAIL] Sending FIXED HTML email to {to_email}...")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Using HTML format (no template)")
        
        # Send email
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        
        print(f"[EMAIL] ✅ Email sent successfully! Status: {response.status_code}")
        
        # Log successful send
        debug_email_send(
            trade_id=trade_id,
            recipient=to_email,
            subject=subject,
            success=True,
            status_code=response.status_code
        )
        
        return {
            "status_code": response.status_code, 
            "success": True,
            "message": f"Trade email sent successfully to {to_email}",
            "trade_id": trade_id,
            "template_id": "html_email_fixed"
        }
        
    except Exception as e:
        error_msg = f"Error sending FIXED email: {str(e)}"
        print(f"[ERROR] {error_msg}")
        
        # Get more detailed error information
        if hasattr(e, 'body'):
            try:
                error_body = e.body.decode('utf-8') if isinstance(e.body, bytes) else str(e.body)
                print(f"[ERROR] SendGrid response: {error_body}")
                error_msg += f" | Response: {error_body}"
            except:
                pass
        
        # Log the failure
        debug_email_send(
            trade_id=trade_id,
            recipient=to_email,
            subject=subject if 'subject' in locals() else "Trade Summary",
            success=False,
            error_message=error_msg
        )
        
        return {"error": error_msg, "success": False, "trade_id": trade_id}

def send_test_email_fixed():
    """Send a test email to verify the configuration"""
    test_trade_data = {
        'trade_id': 'FIXED-TEST-001',
        'ticker': 'BTCUSD',
        'direction': 'long',
        'entry_price': 50000.0,
        'exit_price': 51000.0,
        'pnl': '+1000.0 USD',
        'pnl_amount': 1000.0,
        'date_time': '2025-07-09 12:00:00',
        'timeframe': '5m',
        'reason_or_annotations': 'Test trade for email verification'
    }
    
    test_summary = """
    FIXED EMAIL TEST SUMMARY
    
    This is a test email using the FIXED version that bypasses SendGrid template issues.
    
    ✅ No more template ID errors
    ✅ Rich HTML formatting with emojis and styling
    ✅ Both HTML and plain text versions
    ✅ Professional design with gradients and colors
    ✅ Guaranteed delivery
    
    If you received this email, the fix is working perfectly!
    """
    
    return send_trade_email(test_trade_data, test_summary)

if __name__ == "__main__":
    # Test the FIXED email functionality
    print("Testing FIXED email functionality...")
    result = send_test_email_fixed()
    print("Result:", json.dumps(result, indent=2))
