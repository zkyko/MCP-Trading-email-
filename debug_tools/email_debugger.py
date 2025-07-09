"""
Email Debugging Tool - ASCII ONLY VERSION
Tracks email sending status, logs all attempts, and provides debugging information.
Fixed to prevent Unicode encoding errors.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("email_debugger")

@dataclass
class EmailAttempt:
    """Data class to track email sending attempts"""
    timestamp: str
    trade_id: str
    recipient: str
    subject: str
    success: bool
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None
    template_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'trade_id': self.trade_id,
            'recipient': self.recipient,
            'subject': self.subject,
            'success': self.success,
            'status_code': self.status_code,
            'error_message': self.error_message,
            'response_data': self.response_data,
            'template_id': self.template_id
        }

class EmailDebugger:
    """
    Debug tool to track email sending status and provide detailed logging
    """
    
    def __init__(self, log_file: str = "logs/email_debug.jsonl"):
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging directory and file"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Create file handler for email debug logs
        file_handler = logging.FileHandler(self.log_file.replace('.jsonl', '.log'))
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
    def log_attempt(self, attempt: EmailAttempt):
        """Log an email attempt to both file and console"""
        # Log to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(attempt.to_dict()) + '\n')
            
        # Log to console and log file - ASCII ONLY
        status = "[SUCCESS]" if attempt.success else "[FAILED]"
        logger.info(f"{status} - Trade {attempt.trade_id} - {attempt.recipient}")
        
        if not attempt.success:
            logger.error(f"Error: {attempt.error_message}")
            
    def check_email_config(self) -> Dict[str, Any]:
        """Check if all required email configuration is present"""
        config_status = {
            'sendgrid_api_key': bool(os.getenv('SENDGRID_API_KEY')),
            'from_email': bool(os.getenv('FROM_EMAIL')),
            'to_email': bool(os.getenv('TO_EMAIL')),
            'config_complete': False
        }
        
        config_status['config_complete'] = all([
            config_status['sendgrid_api_key'],
            config_status['from_email'],
            config_status['to_email']
        ])
        
        return config_status
        
    def get_email_stats(self) -> Dict[str, Any]:
        """Get statistics about email sending attempts"""
        if not os.path.exists(self.log_file):
            return {
                'total_attempts': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0,
                'recent_attempts': []
            }
            
        attempts = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    attempts.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
                    
        total = len(attempts)
        successful = sum(1 for a in attempts if a['success'])
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Get recent attempts (last 10)
        recent = sorted(attempts, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        return {
            'total_attempts': total,
            'successful': successful,
            'failed': failed,
            'success_rate': round(success_rate, 2),
            'recent_attempts': recent
        }
        
    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration without sending an actual email"""
        config = self.check_email_config()
        
        test_result = {
            'config_check': config,
            'test_timestamp': datetime.now().isoformat(),
            'recommendations': []
        }
        
        if not config['sendgrid_api_key']:
            test_result['recommendations'].append("Add SENDGRID_API_KEY to your .env file")
            
        if not config['from_email']:
            test_result['recommendations'].append("Add FROM_EMAIL to your .env file")
            
        if not config['to_email']:
            test_result['recommendations'].append("Add TO_EMAIL to your .env file")
            
        if config['config_complete']:
            test_result['recommendations'].append("Configuration looks complete! Try sending a test email.")
            
        return test_result
        
    def print_debug_info(self):
        """Print comprehensive debug information - ASCII ONLY"""
        print("\n" + "="*60)
        print("EMAIL DEBUG INFORMATION")
        print("="*60)
        
        # Configuration check
        config = self.check_email_config()
        print(f"\nConfiguration Status:")
        print(f"   SendGrid API Key: {'YES' if config['sendgrid_api_key'] else 'NO'}")
        print(f"   From Email: {'YES' if config['from_email'] else 'NO'}")
        print(f"   To Email: {'YES' if config['to_email'] else 'NO'}")
        print(f"   Complete: {'YES' if config['config_complete'] else 'NO'}")
        
        # Email statistics
        stats = self.get_email_stats()
        print(f"\nEmail Statistics:")
        print(f"   Total Attempts: {stats['total_attempts']}")
        print(f"   Successful: {stats['successful']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Success Rate: {stats['success_rate']}%")
        
        # Recent attempts
        if stats['recent_attempts']:
            print(f"\nRecent Attempts:")
            for attempt in stats['recent_attempts'][:5]:  # Show last 5
                status = "[OK]" if attempt['success'] else "[FAIL]"
                timestamp = attempt['timestamp'][:19]  # Remove microseconds
                template_info = f" - Template {attempt['template_id']}" if attempt.get('template_id') else ""
                print(f"   {status} {timestamp} - Trade {attempt['trade_id']}{template_info}")
                if not attempt['success'] and attempt['error_message']:
                    print(f"      Error: {attempt['error_message']}")
        
        print("\n" + "="*60)

# Global debugger instance
email_debugger = EmailDebugger()

def debug_email_send(trade_id: str, recipient: str, subject: str, 
                    success: bool, status_code: Optional[int] = None, 
                    error_message: Optional[str] = None, 
                    response_data: Optional[Dict] = None,
                    template_id: Optional[str] = None):
    """
    Convenience function to log email sending attempts
    """
    attempt = EmailAttempt(
        timestamp=datetime.now().isoformat(),
        trade_id=trade_id,
        recipient=recipient,
        subject=subject,
        success=success,
        status_code=status_code,
        error_message=error_message,
        response_data=response_data,
        template_id=template_id
    )
    
    email_debugger.log_attempt(attempt)
    return attempt

if __name__ == "__main__":
    # CLI interface for debugging
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            result = email_debugger.test_email_configuration()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "stats":
            result = email_debugger.get_email_stats()
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "debug":
            email_debugger.print_debug_info()
    else:
        email_debugger.print_debug_info()
