#!/usr/bin/env python3
import argparse
import os
import glob
from engine.utils import setup_logger
from engine.extractor import extract_pdf_text
from engine.excel_engine import ReimbursementExcel
from engine.config import HEADERS

logger = setup_logger("reimbursement_engine")

def process_directory(input_dir, template_path, output_dir):
    logger.info(f"Starting reimbursement processing...")
    logger.info(f"Input: {input_dir}")
    logger.info(f"Template: {template_path}")
    logger.info(f"Output: {output_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Find all PDFs
    pdf_files = glob.glob(os.path.join(input_dir, "**/*.pdf"), recursive=True)
    logger.info(f"Found {len(pdf_files)} PDF files.")

    # 2. Extract text and group by Header (Mocking the categorization for dry-run)
    extracted_data = []
    for pdf in pdf_files:
        text = extract_pdf_text(pdf)
        
        # Simple header detection fallback
        detected_header = "UNKNOWN"
        for header_key, header_val in HEADERS.items():
            if header_val in text:
                detected_header = header_key
                break
                
        extracted_data.append({
            "file": pdf,
            "header": detected_header,
            "text_preview": text[:100].replace('\n', ' ') + "..." if text else ""
        })

    for data in extracted_data:
        logger.info(f"Processed {data['file']} -> Header: {data['header']}")

    # 3. Initialize Excel engines for detected headers
    unique_headers = set([d["header"] for d in extracted_data if d["header"] != "UNKNOWN"])
    
    for header in unique_headers:
        logger.info(f"Generating Excel for header: {header}")
        excel = ReimbursementExcel(template_path)
        
        # Here we would do the actual safe_write logic based on categorized data
        # For this dry run, we just save the empty template with a new name
        
        output_file = os.path.join(output_dir, f"Reimbursement_{header}.xlsx")
        excel.save(output_file)

    logger.info("Processing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corporate Reimbursement Automation Engine")
    parser.add_argument("--input-dir", required=True, help="Directory containing input invoices (PDFs/Images)")
    parser.add_argument("--template", required=True, help="Path to the blank Excel template")
    parser.add_argument("--output-dir", required=True, help="Directory to save generated Excel files")
    
    args = parser.parse_args()
    process_directory(args.input_dir, args.template, args.output_dir)
