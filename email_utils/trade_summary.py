"""
AI-based trade summary generator.
This module uses DeepSeek to generate informative summaries of trade data.
"""

import os
import json
import sys
import requests
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("logs/trade_summary.log"), logging.StreamHandler()]
)
logger = logging.getLogger("trade_summary")

# Load environment variables
load_dotenv()

# Get DeepSeek API configuration
DEEPSEEK_API_KEY = os.getenv("DeepSeek_api_key")
DEEPSEEK_API_BASE = os.getenv("DeepSeek_api_base", "https://api.deepseek.com/v1")

def summarize_trade(trade_data):
    """
    Generate an AI summary of the trade data using DeepSeek.
    
    Args:
        trade_data (dict): Dictionary containing trade information
        
    Returns:
        str: AI-generated summary of the trade
    """
    # Format trade data for the prompt
    trade_str = json.dumps(trade_data, indent=2)
    
    # Create the prompt for DeepSeek
    prompt = f"""
You are a professional trading analyst. Analyze the following trade data and provide a concise, insightful 
summary for the trader. Include assessment of the trade strategy, performance, and any recommendations.

TRADE DATA:
{trade_str}

Your analysis should:
1. Provide a brief overview of the trade (symbol, direction, price points)
2. Analyze the trade's performance
3. Highlight what went well or could be improved
4. Suggest any follow-up actions or patterns to watch for

Write in a professional, concise manner. Use no more than 300 words.
"""
    
    # Call DeepSeek API
    try:
        logger.info("Calling DeepSeek API for trade summary")
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        response = requests.post(
            f"{DEEPSEEK_API_BASE}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
            return f"Error generating trade summary: API returned status {response.status_code}"
        
        response_data = response.json()
        summary = response_data['choices'][0]['message']['content']
        logger.info("Successfully generated trade summary")
        return summary
        
    except Exception as e:
        logger.exception(f"Error generating trade summary: {e}")
        return f"Error generating trade summary: {str(e)}"


def _format_trade_for_prompt(trade_data):
    """Helper to format trade data in a readable way for prompts"""
    
    # Start with basic trade info
    lines = [
        f"Symbol: {trade_data.get('symbol', 'Unknown')}",
        f"Date: {trade_data.get('date', 'Unknown')}",
        f"Type: {trade_data.get('type', 'Unknown').upper()}"
    ]
    
    # Add entry details
    if entry_price := trade_data.get('entry_price'):
        lines.append(f"Entry Price: ${entry_price}")
    
    # Add exit details if available
    if exit_price := trade_data.get('exit_price'):
        lines.append(f"Exit Price: ${exit_price}")
        
        # Calculate P&L if we have both prices
        if entry_price and trade_data.get('type'):
            if trade_data['type'].lower() == 'long':
                pnl_pct = ((float(exit_price) / float(entry_price)) - 1) * 100
                lines.append(f"P&L: {pnl_pct:.2f}%")
            elif trade_data['type'].lower() == 'short':
                pnl_pct = ((float(entry_price) / float(exit_price)) - 1) * 100
                lines.append(f"P&L: {pnl_pct:.2f}%")
    
    # Add any trade notes
    if notes := trade_data.get('notes'):
        lines.append(f"\nNotes: {notes}")
        
    return "\n".join(lines)
