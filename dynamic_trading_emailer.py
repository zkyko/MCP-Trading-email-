"""
Dynamic Trading Email System - FIXED VERSION
No more template dependencies - uses reliable HTML emails
"""

import os
import json
import sys
from datetime import datetime, timedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
from dotenv import load_dotenv

# Load environment
load_dotenv()

class DynamicTradingEmailer:
    """Dynamic email sender that works with live trading data - FIXED VERSION"""
    
    def __init__(self, trade_log_path="logs/trade_log.jsonl"):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL")
        self.to_email = os.getenv("TO_EMAIL")
        self.trade_log_path = trade_log_path
        
    def is_configured(self):
        """Check if email is properly configured"""
        return all([self.api_key, self.from_email, self.to_email])
    
    def clean_text(self, text):
        """Remove any non-ASCII characters that could cause encoding issues"""
        if not text:
            return ""
        return ''.join(char for char in str(text) if 32 <= ord(char) <= 126 or char in '\n\r\t')
    
    def send_email_with_template(self, trade_data, summary):
        """Send email using reliable HTML format (FIXED - no templates)"""
        try:
            if not self.is_configured():
                return {
                    "success": False,
                    "error": "Email not configured. Check SENDGRID_API_KEY, FROM_EMAIL, TO_EMAIL in .env"
                }
            
            # Extract values from trade_data
            symbol = trade_data.get("ticker", "UNKNOWN")
            direction = trade_data.get("direction", "unknown")
            entry_price = trade_data.get("entry_price", "N/A")
            exit_price = trade_data.get("exit_price", "N/A")
            pnl = trade_data.get("pnl", "N/A")
            pnl_amount = trade_data.get("pnl_amount", 0)
            date_time = trade_data.get("date_time", "N/A")
            trade_id = trade_data.get("trade_id", "unknown")
            timeframe = trade_data.get("timeframe", "N/A")
            
            # Clean summary
            cleaned_summary = self.clean_text(summary) if summary else "No summary available"
            
            # Create subject
            profit_status = "PROFIT" if (pnl_amount or 0) > 0 else "INFO"
            subject = f"Trade Alert: {symbol} - {profit_status}"
            
            print(f"[EMAIL] Sending FIXED email for trade {trade_id}...")
            print(f"[EMAIL] Subject: {subject}")
            
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
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Latest Trade Alert</h1>
                        <p>Trade ID: {trade_id}</p>
                    </div>
                    
                    <div class="content">
                        <div class="trade-details">
                            <div class="detail-row">
                                <span class="label">Symbol:</span>
                                <span class="value" style="font-weight: bold; font-size: 16px;">{symbol}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Date & Time:</span>
                                <span class="value">{date_time}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Timeframe:</span>
                                <span class="value">{timeframe}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Direction:</span>
                                <span class="value">{direction.upper() if direction and str(direction) != 'None' else 'N/A'}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Entry Price:</span>
                                <span class="value">${entry_price if entry_price and str(entry_price) != 'None' else 'N/A'}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Exit Price:</span>
                                <span class="value">${exit_price if exit_price and str(exit_price) != 'None' else 'N/A'}</span>
                            </div>
                            
                            <div class="detail-row">
                                <span class="label">Result:</span>
                                <span class="value {('profit' if (pnl_amount or 0) > 0 else 'loss' if (pnl_amount or 0) < 0 else 'neutral')}">{pnl if pnl and str(pnl) != 'None' else 'N/A'}</span>
                            </div>
                        </div>
                        
                        <div class="summary">
                            <h3>AI Analysis Summary</h3>
                            <div class="summary-text">{cleaned_summary}</div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Generated by your Automated Trading Analysis System</p>
                        <p>This email contains AI-generated analysis for informational purposes only.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_content = f"""
            LATEST TRADE ALERT
            ==================
            
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
            """
            
            # Create message
            message = Mail(
                from_email=self.from_email,
                to_emails=self.to_email,
                subject=subject
            )
            
            # Add HTML content
            message.content = [
                Content("text/plain", self.clean_text(text_content)),
                Content("text/html", html_content)
            ]
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            print(f"[EMAIL] ✅ Email sent successfully! Status: {response.status_code}")
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": f"Trade email sent to {self.to_email}",
                "template_id": "html_email_fixed"
            }
            
        except Exception as e:
            error_msg = f"Email failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_latest_trade(self):
        """Get the most recent trade from the log file"""
        try:
            if not os.path.exists(self.trade_log_path):
                return None
            
            with open(self.trade_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            if not lines:
                return None
            
            # Parse the last trade
            last_trade_json = lines[-1].strip()
            return json.loads(last_trade_json)
            
        except Exception as e:
            print(f"Error reading latest trade: {e}")
            return None
    
    def get_all_trades(self):
        """Get all trades from the log file"""
        try:
            if not os.path.exists(self.trade_log_path):
                return []
            
            trades = []
            with open(self.trade_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        trades.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            
            return trades
            
        except Exception as e:
            print(f"Error reading all trades: {e}")
            return []
    
    def get_trading_stats(self):
        """Calculate trading statistics from all trades"""
        trades = self.get_all_trades()
        if not trades:
            return {}
        
        # Calculate stats
        total_trades = len(trades)
        profitable_trades = [t for t in trades if (t.get('pnl_amount') or 0) > 0]
        losing_trades = [t for t in trades if (t.get('pnl_amount') or 0) < 0]
        
        win_rate = (len(profitable_trades) / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t.get('pnl_amount', 0) for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        best_trade = max((t.get('pnl_amount', 0) for t in trades), default=0)
        worst_trade = min((t.get('pnl_amount', 0) for t in trades), default=0)
        
        # Get unique tickers
        tickers = list(set(t.get('ticker') for t in trades if t.get('ticker')))
        
        return {
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'winning_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'total_pnl': round(total_pnl, 2),
            'average_pnl': round(avg_pnl, 2),
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'unique_tickers': len(tickers),
            'tickers': tickers
        }
    
    def send_latest_trade_alert(self):
        """Send email alert for the latest trade using FIXED email"""
        latest_trade = self.get_latest_trade()
        
        if not latest_trade:
            return {"success": False, "error": "No trades found in log"}
        
        # Create summary for the email
        pnl_amount = latest_trade.get('pnl_amount', 0)
        
        summary = f"""
LATEST TRADE ANALYSIS

This trade shows {'positive' if (pnl_amount or 0) > 0 else 'neutral'} performance.

Performance Details:
- Position: {latest_trade.get('direction', 'Unknown').upper()}
- Entry: ${latest_trade.get('entry_price', 'N/A')}
- Exit: ${latest_trade.get('exit_price', 'N/A')}
- Result: {latest_trade.get('pnl', 'N/A')}

{'Congratulations on the profitable trade!' if (pnl_amount or 0) > 0 else 'Trade logged successfully for analysis.'}
        """.strip()
        
        # Send using FIXED email format
        return self.send_email_with_template(latest_trade, summary)

# Quick access functions
def send_latest_trade_email():
    """Quick function to send latest trade email"""
    emailer = DynamicTradingEmailer()
    return emailer.send_latest_trade_alert()

# Command line interface
if __name__ == "__main__":
    print("[MAIN] Dynamic Trading Email System - FIXED VERSION")
    print("=" * 50)
    
    emailer = DynamicTradingEmailer()
    
    # Check configuration
    if not emailer.is_configured():
        print("[ERROR] Email not configured!")
        print("Please check SENDGRID_API_KEY, FROM_EMAIL, TO_EMAIL in .env")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "latest":
            print("Sending latest trade alert...")
            result = emailer.send_latest_trade_alert()
            
        elif command == "test":
            print("Sending test email...")
            test_trade = {
                'trade_id': 'FIXED-TEST-001',
                'ticker': 'BTCUSD',
                'direction': 'long',
                'entry_price': 50000.0,
                'exit_price': 51000.0,
                'pnl': '+1000.0 USD',
                'pnl_amount': 1000.0,
                'date_time': '2025-07-09 12:00:00',
                'timeframe': '5m'
            }
            result = emailer.send_email_with_template(test_trade, "FIXED VERSION TEST - This should work!")
            
        elif command == "stats":
            print("Current trading statistics:")
            stats = emailer.get_trading_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
            sys.exit(0)
            
        else:
            print("Available commands:")
            print("  latest  - Send latest trade alert")
            print("  test    - Send test email")
            print("  stats   - Show trading statistics")
            sys.exit(0)
    else:
        # Default: send latest trade
        print("Sending latest trade alert...")
        result = emailer.send_latest_trade_alert()
    
    # Show result
    if result.get("success"):
        print(f"[SUCCESS] Email sent! Status: {result.get('status_code')}")
        print(f"Message: {result.get('message')}")
    else:
        print(f"[ERROR] Email failed: {result.get('error')}")
