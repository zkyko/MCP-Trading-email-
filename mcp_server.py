# mcp_server.py

import asyncio
import json
import os
from typing import Any
from dotenv import load_dotenv
from pydantic import AnyUrl

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ServerCapabilities

# Load environment variables
load_dotenv()

# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRADE_LOG_PATH = os.path.join(BASE_DIR, "logs", "trade_log.jsonl")

# Ensure logs directory exists
os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)

# Optional failsafe check
if os.path.exists(TRADE_LOG_PATH):
    print(f"[OK] Trade log found at: {TRADE_LOG_PATH}")
else:
    print(f"[WARN] Trade log not found. Creating at: {TRADE_LOG_PATH}")

# === Tool Imports ===
from tools.extract_trade import extract_trade_from_image
from tools.trade import search_trade_logs, get_trade_stats

# Check if email_utils directory exists (renamed from email)
if os.path.exists(os.path.join(os.path.dirname(__file__), "email_utils")):
    # Use email_utils instead of email for our custom email functionality
    email_module_path = "email_utils"
    try:
        from email_utils.sendgrid_client import send_test_email
        from debug_tools.email_debugger import email_debugger
        EMAIL_TOOLS_AVAILABLE = True
        print("[OK] Email tools loaded successfully")
    except ImportError as e:
        print(f"[WARN] Email tools import failed: {e}")
        EMAIL_TOOLS_AVAILABLE = False
elif os.path.exists(os.path.join(os.path.dirname(__file__), "email")):
    # Fall back to email if the directory hasn't been renamed yet
    email_module_path = None
    EMAIL_TOOLS_AVAILABLE = False
    print("[WARN] Warning: 'email' folder conflicts with Python's built-in email module.")
    print("   Consider renaming it to 'email_utils' to avoid import errors.")
else:
    # If neither exists, don't set up email functionality
    email_module_path = None
    EMAIL_TOOLS_AVAILABLE = False

# === Initialize Server ===
server = Server("trading-analysis")

# === Tool List ===
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    tools = [
        Tool(
            name="extract_trade_from_image",
            description="Extract structured trade info from a trading chart screenshot using OCR + LLM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to trading chart image"},
                    "send_email": {"type": "boolean", "description": "Send email notification after processing", "default": False}
                },
                "required": ["image_path"]
            }
        ),
        Tool(
            name="send_latest_trade_email",
            description="Send email alert for the latest trade from your trading log.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="send_all_trades_email",
            description="Send email with complete summary of all trades and statistics.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="send_daily_summary_email",
            description="Send email with summary of trades from the last 24 hours.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_back": {"type": "integer", "description": "Number of days to look back", "default": 1}
                },
                "required": []
            }
        ),
        Tool(
            name="send_direct_email",
            description="Send email directly bypassing all existing email infrastructure.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Email message content"}
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="search_trades",
            description="Search logged trades by term (e.g., ticker, direction).",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                }
            }
        ),
        Tool(
            name="get_trading_stats",
            description="Return aggregated stats from all logged trades.",
            inputSchema={"type": "object", "properties": {}}
        )
    ]
    
    # Add email tools if available
    if EMAIL_TOOLS_AVAILABLE:
        tools.extend([
            Tool(
                name="send_test_email",
                description="Send a test email to verify email configuration.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Custom test message", "default": "Test email from trading system"}
                    }
                }
            ),
            Tool(
                name="get_email_stats",
                description="Get email sending statistics and recent attempts.",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="check_email_config",
                description="Check email configuration status.",
                inputSchema={"type": "object", "properties": {}}
            )
        ])
    
    return tools

# === Tool Execution ===
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    arguments = arguments or {}
    try:
        if name == "extract_trade_from_image":
            image_path = arguments.get("image_path", "")
            send_email = arguments.get("send_email", False)
            if not image_path:
                return [TextContent(type="text", text="[ERROR] image_path is required")]
            
            # Import the enhanced version that supports email
            from tools.enhanced_extract_trade import process_single_image
            result = process_single_image(image_path, save_mode="both", send_email=send_email)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_trades":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 10)
            result = search_trade_logs(query, limit)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_trading_stats":
            result = get_trade_stats()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        # Email tools
        elif name == "send_test_email" and EMAIL_TOOLS_AVAILABLE:
            message = arguments.get("message", "Test email from trading system")
            result = send_test_email(message)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "get_email_stats" and EMAIL_TOOLS_AVAILABLE:
            result = email_debugger.get_email_stats()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "send_latest_trade_email":
            from dynamic_trading_emailer import send_latest_trade_email
            result = send_latest_trade_email()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "send_all_trades_email":
            from dynamic_trading_emailer import send_all_trades_email
            result = send_all_trades_email()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "send_daily_summary_email":
            days_back = arguments.get("days_back", 1)
            from dynamic_trading_emailer import DynamicTradingEmailer
            emailer = DynamicTradingEmailer()
            result = emailer.send_daily_summary(days_back=days_back)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "send_direct_email":
            message = arguments.get("message", "Test message")
            # Import and use direct email function
            from direct_email import send_direct_email
            result = send_direct_email(message)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        elif name == "check_email_config" and EMAIL_TOOLS_AVAILABLE:
            result = email_debugger.check_email_config()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        return [TextContent(type="text", text=f"[ERROR] Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"[ERROR] Error executing {name}: {str(e)}")]

# === Resource Listing ===
@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    if os.path.exists(TRADE_LOG_PATH):
        return [
            Resource(
                uri=AnyUrl(f"file://{TRADE_LOG_PATH}"),
                name="Trade Log",
                description="Complete trade history in JSONL format.",
                mimeType="application/x-jsonlines"
            )
        ]
    return []

# === Resource Reading ===
@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    if str(uri).startswith("file://"):
        file_path = str(uri)[7:]
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return "Unsupported resource URI"

# === Main Entrypoint ===
async def main():
    # Print startup info
    print("[INFO] Starting MCP Trading Analysis Server...")
    print(f"[INFO] Server: trading-analysis v1.0.0")
    print(f"[INFO] Tools: {len(await handle_list_tools())} available")
    print(f"[INFO] Resources: Trade logs and data")
    print("[INFO] Server ready - waiting for connections...")
    print("[INFO] Press Ctrl+C to stop")
    print("-" * 50)
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="trading-analysis",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools={"listChanged": False},
                    resources={"listChanged": False, "subscribe": False}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())