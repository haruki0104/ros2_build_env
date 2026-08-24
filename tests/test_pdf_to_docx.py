"""Tests for the pdf_to_docx.py conversion utility."""

import pymupdf
import pytest

from pdf_to_docx import convert_pdf_to_docx


@pytest.fixture()
def sample_pdf(tmp_path):
    """Create a minimal valid PDF file."""
    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello ROS 2")
    doc.save(pdf_path)
    doc.close()
    return pdf_path


def test_missing_input_returns_false(tmp_path, capsys):
    result = convert_pdf_to_docx(str(tmp_path / "nope.pdf"))
    assert result is False
    assert "does not exist" in capsys.readouterr().err


def test_non_pdf_input_returns_false(tmp_path, capsys):
    txt_file = tmp_path / "file.txt"
    txt_file.write_text("not a pdf")
    assert convert_pdf_to_docx(str(txt_file)) is False
    assert "does not appear to be a PDF" in capsys.readouterr().err


def test_default_output_path(sample_pdf):
    assert convert_pdf_to_docx(str(sample_pdf)) is True
    assert sample_pdf.with_suffix(".docx").exists()


def test_explicit_output_path(sample_pdf, tmp_path):
    output = tmp_path / "out" / "custom.docx"
    output.parent.mkdir()
    assert convert_pdf_to_docx(str(sample_pdf), str(output)) is True
    assert output.exists()
