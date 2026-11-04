"""Statement processing, review, and export endpoints."""

from datetime import datetime, timezone
from pathlib import Path
import uuid
from typing import BinaryIO, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
import pikepdf
from pydantic import BaseModel

from app.errors import ErrorCode, ProcessingError
from app.pipeline.intake import process_intake, cleanup_intake_file
from app.pipeline.pdf_type import detect_document_type, PageType
from app.pipeline.native_extract import extract_native_words_from_document
from app.pipeline.ocr.tesseract import default_ocr_engine
from app.pipeline.layout.words import cluster_words_into_lines, Word
from app.pipeline.layout.table_detector import detect_table_header
from app.pipeline.layout.row_builder import reconstruct_transaction_rows
from app.pipeline.parse.dates import parse_date
from app.pipeline.parse.amounts import parse_amount
from app.pipeline.parse.metadata import extract_metadata_from_text
from app.pipeline.validate.reconcile import validate_and_reconcile_transactions
from app.classification.hybrid import default_hybrid_classifier
from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.core.storage import statement_store, StatementRecord, StatementSummary
from app.export.csv_exporter import export_transactions_to_csv
from app.export.xlsx_exporter import export_transactions_to_xlsx
from app.errors import ProcessingError

router = APIRouter(prefix="/statements", tags=["Statements"])


class CategoryUpdateRequest(BaseModel):
    category: str


def execute_pipeline(
    file_stream: BinaryIO, filename: str, password: Optional[str] = None
) -> StatementRecord:
    """Core processing pipeline converting PDF stream to fully classified and validated StatementRecord."""
    # 1. Intake validation & secure temporary persistence
    intake_res = process_intake(file_stream, filename)
    working_path = intake_res.file_path

    # Handle password-protected encrypted PDFs
    if intake_res.needs_password:
        if not password:
            cleanup_intake_file(intake_res.file_path)
            raise ProcessingError(
                code=ErrorCode.PDF_ENCRYPTED,
                message="This bank statement is password-protected. Please enter your statement password to decrypt it.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            decrypted_path = intake_res.file_path.with_suffix(".decrypted.pdf")
            with pikepdf.Pdf.open(intake_res.file_path, password=password) as enc_pdf:
                enc_pdf.save(decrypted_path)
            cleanup_intake_file(intake_res.file_path)
            working_path = decrypted_path
        except pikepdf.PasswordError:
            cleanup_intake_file(intake_res.file_path)
            raise ProcessingError(
                code=ErrorCode.WRONG_PASSWORD,
                message="The password provided is incorrect. Please check and try again.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    # 2. Page-level PDF type detection
    doc_report = detect_document_type(working_path)

    # 3. Word extraction (Native text for digital pages, OCR for scanned pages)
    all_words: List[Word] = []
    for page_metric in doc_report.pages:
        p_num = page_metric.page_number
        if page_metric.page_type == PageType.DIGITAL:
            page_words = extract_native_words_from_document(
                working_path, pages_to_extract=[p_num]
            )
            all_words.extend(page_words)
        else:
            ocr_words = default_ocr_engine.ocr_page(working_path, p_num)
            all_words.extend(ocr_words)

    # 4. Line clustering & Table header detection
    lines = cluster_words_into_lines(all_words)
    header = detect_table_header(lines)

    raw_rows = []
    if header:
        raw_rows = reconstruct_transaction_rows(lines, header)

    # 5. Normalization
    normalized_txns: List[NormalizedTransaction] = []
    for r in raw_rows:
        parsed_d, d_flags = parse_date(r.date_raw)
        deb_amt, curr1, deb_flags = parse_amount(r.debit_raw)
        cred_amt, curr2, cred_flags = parse_amount(r.credit_raw)
        bal_amt, curr3, bal_flags = parse_amount(r.balance_raw)

        combined_flags = list(set(d_flags + deb_flags + cred_flags + bal_flags))

        normalized_txns.append(
            NormalizedTransaction(
                id=str(uuid.uuid4()),
                statement_id=intake_res.file_id,
                line_number=r.line_number,
                page_number=r.page_number,
                date=parsed_d,
                date_raw=r.date_raw,
                description=r.description_raw,
                description_raw=r.description_raw,
                ref_no=r.ref_raw,
                debit=deb_amt,
                credit=cred_amt,
                balance=bal_amt,
                currency=curr1 or curr2 or curr3 or "AUD",
                raw_debit=r.debit_raw,
                raw_credit=r.credit_raw,
                raw_balance=r.balance_raw,
                flags=combined_flags,
                row_confidence=r.confidence,
                bounding_box=r.bounding_box,
            )
        )

    # 6. Extract Statement & Account Metadata
    full_text = "\n".join([line.text for line in lines])
    stmt_meta = extract_metadata_from_text(full_text)

    # 7. Balance validation & reconciliation
    from decimal import Decimal, InvalidOperation
    open_dec: Optional[Decimal] = None
    close_dec: Optional[Decimal] = None
    if stmt_meta.opening_balance:
        try:
            open_dec = Decimal(stmt_meta.opening_balance.replace(",", ""))
        except (InvalidOperation, TypeError):
            pass
    if stmt_meta.closing_balance:
        try:
            close_dec = Decimal(stmt_meta.closing_balance.replace(",", ""))
        except (InvalidOperation, TypeError):
            pass

    reconciled_txns, recon_summary = validate_and_reconcile_transactions(
        normalized_txns,
        opening_balance=open_dec,
        closing_balance=close_dec,
    )

    # 8. Non-LLM hybrid classification
    classified_txns = default_hybrid_classifier.classify_all(reconciled_txns)

    # 9. Persist statement record
    record = StatementRecord(
        id=intake_res.file_id,
        filename=intake_res.original_filename,
        sha256=intake_res.sha256,
        file_size_bytes=intake_res.file_size_bytes,
        page_count=intake_res.page_count,
        doc_type_report=doc_report,
        reconciliation_summary=recon_summary,
        transactions=classified_txns,
        metadata=stmt_meta,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    statement_store.save(record)

    # Clean temporary working file
    cleanup_intake_file(working_path)

    return record


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_and_process_statement(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None),
):
    """Upload a bank statement PDF and execute full extraction, reconciliation, and classification."""
    try:
        return execute_pipeline(file.file, file.filename or "statement.pdf", password=password)
    except ProcessingError as pe:
        raise HTTPException(status_code=pe.status_code, detail=pe.to_problem_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


SAMPLE_MAP = {
    "cba": ("cba_australian_statement.pdf", "CBA_AU_October_2023.pdf"),
    "barclays": ("barclays_uk_statement.pdf", "Barclays_UK_October_2023.pdf"),
    "westpac": ("westpac_australian_statement.pdf", "Westpac_AU_November_2023.pdf"),
    "sbi": ("sbi_india_statement.pdf", "SBI_India_October_2023.pdf"),
    "encrypted": ("encrypted_cba_statement.pdf", "Protected_CBA_Statement.pdf"),
    "au100": ("au_100_scanned_statement.pdf", "AU_100_transactions_scanned.pdf"),
}


def get_samples_dir() -> Path:
    """Find samples directory across local and Docker container environments."""
    candidates = [
        Path("data/samples"),
        Path("/app/data/samples"),
        Path("d:/beFree/data/samples"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return Path("data/samples")


@router.post("/samples/{sample_key}", status_code=status.HTTP_201_CREATED)
async def load_sample_statement(sample_key: str, password: Optional[str] = Query(None)):
    """Load and process a pre-bundled synthetic sample statement (cba, barclays, westpac, sbi, encrypted)."""
    if sample_key not in SAMPLE_MAP:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown sample key.")

    sample_filename, display_name = SAMPLE_MAP[sample_key]
    file_path = get_samples_dir() / sample_filename

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample PDF not found.")

    try:
        with open(file_path, "rb") as f:
            return execute_pipeline(f, display_name, password=password)
    except ProcessingError as pe:
        raise HTTPException(status_code=pe.status_code, detail=pe.to_problem_dict())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": str(e)},
        )


@router.get("/samples/{sample_key}/download")
async def download_sample_pdf(sample_key: str):
    """Directly download the synthetic bank statement PDF for local testing."""
    if sample_key not in SAMPLE_MAP:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown sample key.")

    sample_filename, display_name = SAMPLE_MAP[sample_key]
    file_path = get_samples_dir() / sample_filename

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample PDF not found.")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=display_name,
    )


@router.get("", response_model=List[StatementSummary])
async def list_statements():
    """List all processed statements in descending chronological order."""
    return statement_store.list_summaries()


@router.get("/{statement_id}")
async def get_statement_details(statement_id: str):
    """Retrieve processed statement metadata and summary."""
    record = statement_store.get(statement_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found.")
    return record


@router.delete("/{statement_id}")
async def delete_statement(statement_id: str):
    """Delete a processed statement and all its transactions."""
    success = statement_store.delete(statement_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found.")
    return {"status": "deleted", "id": statement_id}


@router.get("/{statement_id}/transactions")
async def list_statement_transactions(
    statement_id: str,
    q: Optional[str] = Query(None, description="Search description text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    flag: Optional[str] = Query(None, description="Filter by flag (e.g. LOW_CONFIDENCE)"),
):
    """List transactions with filtering by search query, category, and review flags."""
    record = statement_store.get(statement_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found.")

    txns = record.transactions
    if q:
        query_upper = q.upper()
        txns = [t for t in txns if query_upper in t.description.upper()]
    if category:
        txns = [t for t in txns if t.category == category]
    if flag:
        txns = [t for t in txns if flag in t.flags]

    return {"statement_id": statement_id, "total": len(txns), "transactions": txns}


@router.patch("/{statement_id}/transactions/{transaction_id}")
async def correct_transaction_category(
    statement_id: str,
    transaction_id: str,
    payload: CategoryUpdateRequest,
):
    """Correct transaction category with manual audit trail."""
    updated = statement_store.update_transaction(
        statement_id, transaction_id, new_category=payload.category
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found."
        )
    return updated


@router.get("/{statement_id}/export/csv")
async def export_statement_csv(statement_id: str):
    """Stream CSV export of reviewed transactions with formula injection defense."""
    record = statement_store.get(statement_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found.")

    csv_bytes = export_transactions_to_csv(record.transactions)
    filename = f"{record.filename.rsplit('.', 1)[0]}_export.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{statement_id}/export/xlsx")
async def export_statement_xlsx(statement_id: str):
    """Stream Excel (.xlsx) export of reviewed transactions with summary sheet."""
    record = statement_store.get(statement_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found.")

    detected_bank = (
        record.metadata.bank_name
        if record.metadata and record.metadata.bank_name
        else "Bank Statement"
    )
    detected_account = (
        record.metadata.account_number
        if record.metadata and record.metadata.account_number
        else None
    )

    xlsx_bytes = export_transactions_to_xlsx(
        record.transactions,
        bank_name=detected_bank,
        account_number=detected_account,
        quality_score=record.reconciliation_summary.quality_score,
    )
    filename = f"{record.filename.rsplit('.', 1)[0]}_export.xlsx"

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
