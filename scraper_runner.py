import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, cast
from scraper import IndiabixScraper
from translator import translate_questions_with_ai
from pdf_generator import PDFGenerator
from pdf_generator_compact import PDFGeneratorCompact
from config import PDF_OUTPUT_DIR, WATERMARK_FILENAME

class CallbackHandler(logging.Handler):
    """Sends every log record to a callback(str)."""
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord):
        try:
            self.callback(self.format(record))
        except Exception:
            pass

class ScrapingPipeline:
    """Manages the end-to-end execution of scraping, translating, and PDF generation."""
    
    def __init__(self, scraper, log_callback: Optional[Callable[[str], None]] = None):
        self.scraper = scraper
        self.log_callback = log_callback
        
        # Setup specific logger instead of root logger to prevent library spam
        self.logger = logging.getLogger("scraper_pipeline")
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger just for this pipeline execution
        self.logger.propagate = False
        
        self.cb_handler: Optional[CallbackHandler] = None
        if log_callback:
            # Clear existing handlers first
            self.logger.handlers.clear()
            self.cb_handler = CallbackHandler(log_callback)
            handler = cast(logging.Handler, self.cb_handler)
            handler.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))
            self.logger.addHandler(handler)
            
            # Also attach it to the scraper logger so we see scraper logs
            scraper_logger = logging.getLogger("scraper")
            scraper_logger.handlers.clear()
            scraper_logger.addHandler(handler)
            scraper_logger.propagate = False

    def log(self, msg: str):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def run(self, date_obj: datetime) -> dict:
        result = {
            "success": False,
            "questions_count": 0,
            "date": date_obj.strftime("%Y-%m-%d"),
            "pdf_detailed": None,
            "pdf_compact": None,
            "json_english": None,
            "json_gujarati": None,
            "error": None,
        }

        try:
            date_str = date_obj.strftime("%Y-%m-%d")
            self.log(f"selected date : {date_str}")
            self.log("─" * 50)

            # 1. Scrape
            self.log("step 1/3 — scraping...")
            questions_en = self.scraper.scrape_date(date_obj)

            if not questions_en:
                result["error"] = f"no questions found for {date_str}. the page may not exist yet."
                self.log(str(result["error"]))
                return result

            self.log(f"scraped {len(questions_en)} questions")
            result["questions_count"] = len(questions_en)

            # 2. Translate
            self.log("step 2/3 — translating to gujarati (ai)...")
            self.log("this may take a few minutes...")
            questions_gu = translate_questions_with_ai(questions_en)
            
            if not questions_gu:
                result["error"] = "translation failed, no questions to process further."
                self.log(result["error"])
                return result
                
            self.log(f"translation complete — {len(questions_gu)} questions ready")

            # 3. Save JSONs
            script_dir = Path(__file__).parent
            output_dir = script_dir / PDF_OUTPUT_DIR
            output_dir.mkdir(exist_ok=True)

            json_en_path = output_dir / "questions_english.json"
            json_gu_path = output_dir / "questions_gujarati.json"

            with open(json_en_path, "w", encoding="utf-8") as f:
                json.dump(questions_en, f, ensure_ascii=False, indent=2)
            with open(json_gu_path, "w", encoding="utf-8") as f:
                json.dump(questions_gu, f, ensure_ascii=False, indent=2)

            result["json_english"] = str(json_en_path)
            result["json_gujarati"] = str(json_gu_path)
            self.log(f"json files saved to {PDF_OUTPUT_DIR}/")

            # 4. Generate PDFs
            self.log("step 3/3 — generating pdfs...")
            watermark_path = script_dir / WATERMARK_FILENAME
            watermark = str(watermark_path) if watermark_path.exists() else None

            try:
                # detailed pdf
                gen_detailed = PDFGenerator(
                    output_dir=str(output_dir), language="gu", watermark_image=watermark,
                )
                pdf_detailed = gen_detailed.generate_pdf(
                    questions_gu, start_date=date_str, end_date=date_str
                )
                if pdf_detailed:
                    result["pdf_detailed"] = pdf_detailed
                    self.log(f"detailed pdf -> {Path(pdf_detailed).name}")

                # compact pdf
                gen_compact = PDFGeneratorCompact(
                    output_dir=str(output_dir), language="gu", watermark_image=watermark,
                )
                pdf_compact = gen_compact.generate_pdf(
                    questions_gu, start_date=date_str, end_date=date_str
                )
                if pdf_compact:
                    result["pdf_compact"] = pdf_compact
                    self.log(f"compact pdf  -> {Path(pdf_compact).name}")

            except Exception as pdf_exc:
                self.log(f"pdf generation failed: {pdf_exc}")

            self.log("─" * 50)
            self.log(f"pipeline complete! {len(questions_gu)} questions processed.")
            result["success"] = True

        except Exception as exc:
            result["error"] = str(exc)
            self.log(f"Error: {exc}\n{traceback.format_exc()}")

        finally:
            # Clean up handlers
            if self.cb_handler:
                clean_handler = cast(logging.Handler, self.cb_handler)
                self.logger.removeHandler(clean_handler)
                scraper_logger = logging.getLogger("scraper")
                scraper_logger.removeHandler(clean_handler)

        return result


# Backwards compatible wrapper for app.py with Smart Lookback
def run_pipeline(
    date_obj: datetime,
    log_callback: Optional[Callable[[str], None]] = None,
    lookback_days: int = 5
) -> dict:
    import datetime as dt
    scraper = IndiabixScraper()
    pipeline = ScrapingPipeline(scraper=scraper, log_callback=log_callback)
    
    # Try the initial date
    result = pipeline.run(date_obj)
    
    # Smart Lookback: If no questions found, try previous days
    if not result.get("success") and "no questions found" in str(result.get("error", "")).lower():
        pipeline.log(f"Smart Lookback: No questions on {date_obj.strftime('%Y-%m-%d')}. Searching previous days...")
        
        current_date = date_obj
        for i in range(1, lookback_days + 1):
            current_date = current_date - dt.timedelta(days=1)
            pipeline.log(f"Checking {current_date.strftime('%Y-%m-%d')} (Lookback {i}/{lookback_days})...")
            
            # Reset pipeline log handlers for the new run if needed (though they should stay attached)
            new_result = pipeline.run(current_date)
            
            if new_result.get("success"):
                pipeline.log(f"✓ Found latest questions from {current_date.strftime('%Y-%m-%d')}!")
                return new_result
            
            # If it's a real error (not just empty), stop
            if "no questions found" not in str(new_result.get("error", "")).lower():
                return new_result
                
    return result
