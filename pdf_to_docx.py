#!/usr/bin/env python3
import argparse
import os
import sys

from pdf2docx import Converter


def convert_pdf_to_docx(pdf_path, docx_path=None, start_page=0, end_page=None):
    """
    Converts a PDF file to DOCX format, which can be opened directly by macOS Pages or Microsoft Word.
    """
    # Resolve absolute paths
    pdf_path = os.path.abspath(pdf_path)

    if not os.path.exists(pdf_path):
        print(f"Error: The input file '{pdf_path}' does not exist.", file=sys.stderr)
        return False

    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: The input file '{pdf_path}' does not appear to be a PDF file.", file=sys.stderr)
        return False

    if docx_path is None:
        docx_path = os.path.splitext(pdf_path)[0] + '.docx'
    else:
        docx_path = os.path.abspath(docx_path)

    print(f"Converting PDF:  {pdf_path}")
    print(f"To Word DOCX:   {docx_path}")

    try:
        # Initialize the converter
        cv = Converter(pdf_path)

        # Convert the file (start_page is 0-indexed, end_page is exclusive)
        # Setting end_page=None converts until the last page
        cv.convert(docx_path, start=start_page, end=end_page)

        # Close the converter
        cv.close()

        print("\nConversion successfully completed!")
        print(f"You can now open '{docx_path}' in macOS Pages or Microsoft Word.")
        return True
    except Exception as e:
        print(f"\nAn error occurred during conversion: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Convert a PDF document into a Word (.docx) format file compatible with macOS Pages."
    )
    parser.add_argument("pdf_file", help="Path to the source PDF file to convert.")
    parser.add_argument("-o", "--output",
                        help="Optional output path for the Word (.docx) file. "
                             "Defaults to the same name and directory.")
    parser.add_argument("-s", "--start", type=int, default=0, help="Start page index (0-indexed, default: 0).")
    parser.add_argument("-e", "--end", type=int, default=None, help="End page index (exclusive, default: convert all).")

    args = parser.parse_args()

    success = convert_pdf_to_docx(
        pdf_path=args.pdf_file,
        docx_path=args.output,
        start_page=args.start,
        end_page=args.end
    )
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
