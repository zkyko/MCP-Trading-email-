"""
enhanced_extract_trade.py
AI-powered trade extractor with single-image and batch support,
OCR confidence metrics, DeepSeek integration, and multi-format logging.

Usage examples (CLI):
    python enhanced_extract_trade.py trade.png
    python enhanced_extract_trade.py screenshots/ --batch
    python enhanced_extract_trade.py trade.png --json-only
"""

# ---------- IMPORTS ----------
import os, sys, json, uuid, re
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, field_validator
from PIL import Image
import pytesseract
from openai import OpenAI

load_dotenv()

# Import email functionality
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'email_utils'))
    from sendgrid_client import send_trade_email
    from trade_summary import summarize_trade
    EMAIL_ENABLED = True
    print("[OK] Email functionality loaded successfully")
except ImportError as e:
    print(f"[WARN] Email functionality not available: {e}")
    EMAIL_ENABLED = False

# === Path Configuration ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADE_LOG_PATH = os.path.join(BASE_DIR, "logs", "trade_log.jsonl")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")

# ---------- OPENAI / DEEPSEEK CLIENT ----------
client = OpenAI(
    api_key=os.getenv("DeepSeek_api_key") or os.getenv("DEEPSEEK_API_KEY"),     # support both naming conventions
    base_url=os.getenv("DeepSeek_api_base") or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
)

# ---------- DATA SCHEMAS ----------
class TradeData(BaseModel):
    trade_id: str
    ticker: Optional[str] = None
    timeframe: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    direction: Optional[str] = None
    pnl: Optional[str] = None
    pnl_amount: Optional[float] = None
    date_time: Optional[str] = None
    reason_or_annotations: Optional[str] = None
    image_source: Optional[str] = None
    logged_at: str
    ocr_confidence: Optional[str] = None

    @field_validator('pnl_amount', mode='before')
    @classmethod
    def parse_pnl_amount(cls, v):
        """Parse PnL amount from various string formats"""
        if v is None or v == "":
            return None
        
        if isinstance(v, (int, float)):
            return float(v)
        
        if isinstance(v, str):
            # Remove common symbols and clean the string
            cleaned = re.sub(r'[^\d\.\-\+]', '', v.replace(',', ''))
            if cleaned:
                try:
                    return float(cleaned)
                except ValueError:
                    return None
        
        return None

# ---------- OCR ----------
def extract_text_from_image(image_path: str) -> Tuple[str, Dict]:
    """OCR text + confidence info"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    # raw text
    text = pytesseract.image_to_string(img)
    # word-level data for confidence
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    # Fixed confidence parsing
    confs = []
    for c in data["conf"]:
        try:
            conf_val = int(c)
            if conf_val > 0:
                confs.append(conf_val)
        except (ValueError, TypeError):
            continue
    
    avg_conf = sum(confs) / len(confs) if confs else 0.0

    return text, {
        "confidence": avg_conf,
        "total_words": len([w for w in data["text"] if w.strip()]),
        "image_size": img.size,
    }

# ---------- AI ANALYSIS ----------
def analyze_trade_with_ai(raw_text: str, image_path: str) -> str:
    """Call DeepSeek (OpenAI-compatible) to structure the trade"""
    prompt = f"""
You are an expert trading analyst. Given OCR text from a trading screenshot, output ONLY valid JSON with the following keys:

ticker, timeframe, entry_price, exit_price, direction, pnl, pnl_amount, date_time, reason_or_annotations

IMPORTANT: For pnl_amount, extract only the numeric value (e.g., if you see "+38.07 USD", output 38.07)

OCR text from {os.path.basename(image_path)}:
\"\"\"{raw_text}\"\"\"

Example output:
{{
  "ticker": "SOLUSD",
  "timeframe": "5m",
  "entry_price": 150.25,
  "exit_price": 151.50,
  "direction": "long",
  "pnl": "+38.07 USD",
  "pnl_amount": 38.07,
  "date_time": "2025-07-06 14:20:58",
  "reason_or_annotations": "Quick scalp trade"
}}
"""
    
    print("[API] Sending request to DeepSeek...")
    print(f"[API] Base URL: {os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com')}")
    print(f"[API] Key set: {'Yes' if os.getenv('DEEPSEEK_API_KEY') else 'No'}")
    print(f"[API] Prompt length: {len(prompt)} characters")
    
    try:
        import httpx
        import time
        start_time = time.time()
        
        # Use httpx for better timeout control
        headers = {
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        print(f"[API] Model: {payload['model']}")
        print(f"[API] Timeout: 30 seconds")
        
        with httpx.Client(timeout=30.0) as client_http:
            response = client_http.post(
                os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com') + "/chat/completions",
                headers=headers,
                json=payload
            )
            
            elapsed = time.time() - start_time
            print(f"[API] Request completed in {elapsed:.2f}s")
            print(f"[API] Response status: {response.status_code}")
            
            response.raise_for_status()
            result = response.json()
            print(f"[API] Response received: {len(str(result))} characters")
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"[API] Content length: {len(content)} characters")
                return content
            else:
                print(f"[API] Unexpected response format: {result}")
                return '{"error": "Unexpected API response format"}'
                
    except httpx.TimeoutException:
        print("[ERROR] Request timed out after 30 seconds")
        return '{"error": "API request timed out", "ticker": "UNKNOWN", "direction": "unknown", "pnl_amount": 0}'
    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HTTP error {e.response.status_code}: {e.response.text}")
        return '{"error": "API HTTP error", "ticker": "UNKNOWN", "direction": "unknown", "pnl_amount": 0}'
    except Exception as e:
        print(f"[ERROR] Unexpected error during DeepSeek API call: {str(e)}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        return '{"error": "API call failed", "ticker": "UNKNOWN", "direction": "unknown", "pnl_amount": 0}'
    
    # Fallback - should not reach here
    print("[ERROR] Reached unexpected fallback")
    return '{"error": "Unexpected fallback", "ticker": "UNKNOWN", "direction": "unknown", "pnl_amount": 0}'

# ---------- RECORD CREATION ----------
def create_trade_record(ai_json: str, image_path: str, ocr_info: Dict) -> TradeData:
    # strip optional back-ticks
    cleaned = ai_json.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:-3].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:-3].strip()

    try:
        data = json.loads(cleaned)
        print(f"[DATA] Parsed AI data: {data}")  # Debug logging
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse error: {e}")
        data = {"error": f"JSON parse error: {e}"}

    return TradeData(
        trade_id=str(uuid.uuid4())[:8],
        ticker=data.get("ticker"),
        timeframe=data.get("timeframe"),
        entry_price=data.get("entry_price"),
        exit_price=data.get("exit_price"),
        direction=data.get("direction"),
        pnl=data.get("pnl"),
        pnl_amount=data.get("pnl_amount"),
        date_time=data.get("date_time"),
        reason_or_annotations=data.get("reason_or_annotations"),
        image_source=os.path.basename(image_path),
        logged_at=datetime.now().isoformat(),
        ocr_confidence=f"{ocr_info.get('confidence', 0):.1f}%",
    )

# ---------- SAVE LOGS ----------
def save_trade_data(trade: TradeData, mode: str = "both") -> List[str]:
    saved: List[str] = []

    # 1. append to JSONL database
    os.makedirs(os.path.dirname(TRADE_LOG_PATH), exist_ok=True)
    with open(TRADE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(trade.model_dump_json() + "\n")
    saved.append(TRADE_LOG_PATH)

    # 2. individual JSON
    if mode in {"both", "json"}:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        fp = os.path.join(
            OUTPUT_DIR, f"trade_{trade.trade_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        )
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(trade.model_dump(), f, indent=2, default=str)
        saved.append(fp)

    # 3. daily summary
    if mode in {"both", "jsonl"}:
        day = datetime.now().strftime("%Y-%m-%d")
        summary_path = os.path.join(SUMMARIES_DIR, f"daily_summary_{day}.json")
        os.makedirs(SUMMARIES_DIR, exist_ok=True)
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
        else:
            summary = {
                "date": day,
                "trades": [],
                "total_trades": 0,
                "total_pnl": 0,
                "created_at": datetime.now().isoformat(),
            }
        summary["trades"].append(trade.model_dump())
        summary["total_trades"] = len(summary["trades"])
        summary["total_pnl"] = sum(t.get("pnl_amount") or 0 for t in summary["trades"])
        summary["updated_at"] = datetime.now().isoformat()
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, default=str)
        saved.append(summary_path)

    return saved

# ---------- SINGLE IMAGE ----------
def process_single_image(image_path: str, save_mode: str = "both", send_email: bool = False) -> Dict:
    try:
        print(f"[OCR] Starting extraction for: {image_path}")
        raw_text, ocr_info = extract_text_from_image(image_path)
        print(f"[OCR] Completed, confidence: {ocr_info['confidence']:.1f}%")
        
        print(f"[AI] Calling analysis...")
        ai_json = analyze_trade_with_ai(raw_text, image_path)
        print(f"[AI] Response received")
        
        print(f"[DATA] Creating trade record...")
        trade = create_trade_record(ai_json, image_path, ocr_info)
        print(f"[SAVE] Saving trade data...")
        files = save_trade_data(trade, save_mode)
        
        result = {
            "trade_id": trade.trade_id,
            "image": os.path.basename(image_path),
            "ticker": trade.ticker,
            "direction": trade.direction,
            "pnl_amount": trade.pnl_amount,
            "confidence": ocr_info["confidence"],
            "saved_files": files,
            "email_sent": False,
            "email_status": "Email disabled or not requested"
        }
        
        # Send email if requested and enabled
        if send_email and EMAIL_ENABLED:
            print(f"[EMAIL] Generating summary...")
            try:
                # Generate AI summary for email
                email_summary = summarize_trade(trade.model_dump())
                print(f"[EMAIL] Sending trade email...")
                
                # Send email
                email_result = send_trade_email(trade.model_dump(), email_summary)
                
                result["email_sent"] = email_result.get("success", False)
                result["email_status"] = email_result.get("message", email_result.get("error", "Unknown status"))
                result["email_details"] = email_result
                
                if email_result.get("success"):
                    print(f"[EMAIL] Sent successfully!")
                else:
                    print(f"[EMAIL] Failed: {email_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"[EMAIL] Error: {str(e)}")
                result["email_sent"] = False
                result["email_status"] = f"Email error: {str(e)}"
                
        elif send_email and not EMAIL_ENABLED:
            result["email_status"] = "Email functionality not available"
            
        # Auto-send email for successful trades (Method 2 Integration)
        if send_email and EMAIL_ENABLED and trade.pnl_amount:
            try:
                print(f"[AUTO-EMAIL] Sending trade alert...")
                from dynamic_trading_emailer import DynamicTradingEmailer
                emailer = DynamicTradingEmailer()
                auto_email_result = emailer.send_latest_trade_alert()
                result["auto_email_sent"] = auto_email_result.get("success", False)
                result["auto_email_status"] = auto_email_result.get("message", auto_email_result.get("error", "Unknown status"))
                
                if auto_email_result.get("success"):
                    print(f"[AUTO-EMAIL] Trade alert sent successfully!")
                else:
                    print(f"[AUTO-EMAIL] Failed: {auto_email_result.get('error')}")
                    
            except Exception as e:
                print(f"[AUTO-EMAIL] Error: {str(e)}")
                result["auto_email_sent"] = False
                result["auto_email_status"] = f"Auto-email error: {str(e)}"
        else:
            result["auto_email_sent"] = False
            if not send_email:
                result["auto_email_status"] = "Auto-email not requested"
            elif not EMAIL_ENABLED:
                result["auto_email_status"] = "Email functionality not available"
            elif not trade.pnl_amount:
                result["auto_email_status"] = "No P&L amount detected for email"
            
        print(f"[SUCCESS] Processing complete")
        return result
        
    except Exception as e:
        print(f"[ERROR] Error in process_single_image: {str(e)}")
        raise

# ---------- BATCH ----------
def process_multiple_images(folder: str, save_mode: str = "both", send_email: bool = False) -> Dict:
    if not os.path.isdir(folder):
        return {"error": f"Folder not found: {folder}"}

    exts = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}
    images = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(tuple(exts))]
    if not images:
        return {"error": "No image files found"}

    results = {
        "total": len(images), 
        "ok": 0, 
        "fail": 0, 
        "details": [],
        "emails_sent": 0,
        "email_failures": 0
    }
    
    for img in images:
        try:
            res = process_single_image(img, save_mode, send_email)
            results["details"].append(res)
            results["ok"] += 1
            
            # Track email statistics
            if send_email:
                if res.get("email_sent", False):
                    results["emails_sent"] += 1
                else:
                    results["email_failures"] += 1
                    
        except Exception as e:
            error_result = {"image": os.path.basename(img), "error": str(e)}
            if send_email:
                error_result["email_sent"] = False
                error_result["email_status"] = "Processing failed before email"
                results["email_failures"] += 1
            results["details"].append(error_result)
            results["fail"] += 1
            
    return results

# ---------- CLI ENTRY ----------
def _cli():
    if len(sys.argv) < 2:
        print("Usage: python enhanced_extract_trade.py <image>|<folder> [--batch] [--json-only|--jsonl-only] [--send-email]")
        print("Options:")
        print("  --batch       Process folder of images")
        print("  --json-only   Save only individual JSON files")
        print("  --jsonl-only  Save only to JSONL database")
        print("  --send-email  Auto-send email alerts for processed trades")
        print("")
        print("Auto-Email Features:")
        print("  - Automatically sends trade alerts after successful processing")
        print("  - Uses live data from your trade log")
        print("  - Only sends emails for trades with P&L amounts")
        print("  - ASCII-only content to prevent encoding errors")
        sys.exit(1)

    target = sys.argv[1]
    batch = "--batch" in sys.argv or os.path.isdir(target)
    send_email = "--send-email" in sys.argv
    mode = "both"
    if "--json-only" in sys.argv: mode = "json"
    if "--jsonl-only" in sys.argv: mode = "jsonl"

    if send_email and not EMAIL_ENABLED:
        print("[WARN] Email functionality is not available. Proceeding without email.")
        send_email = False

    if batch:
        print(f"[BATCH] Processing folder: {target}")
        if send_email:
            print("[EMAIL] Auto-email notifications enabled for each trade")
        result = process_multiple_images(target, mode, send_email)
        print(json.dumps(result, indent=2))
    else:
        if send_email:
            print("[EMAIL] Auto-email notifications enabled")
        result = process_single_image(target, mode, send_email)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    _cli()
