"""Persistent SQLite statement repository backed by SQLAlchemy 2 with WAL mode."""

import json
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel
from sqlalchemy import select

from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.pipeline.pdf_type import DocumentTypeReport
from app.pipeline.validate.reconcile import ReconciliationSummary
from app.pipeline.parse.metadata import StatementMetadata
from app.core.database import SessionLocal, StatementModel, TransactionModel, init_db


class StatementRecord(BaseModel):
    """Processed statement record stored in the repository."""

    id: str
    filename: str
    sha256: str
    file_size_bytes: int
    page_count: int
    doc_type_report: DocumentTypeReport
    reconciliation_summary: ReconciliationSummary
    transactions: List[NormalizedTransaction]
    metadata: Optional[StatementMetadata] = None
    created_at: str


class StatementSummary(BaseModel):
    """Lightweight metadata summary for statement history lists."""

    id: str
    filename: str
    file_size_bytes: int
    page_count: int
    created_at: str
    currency: str
    transaction_count: int
    quality_score: float
    statement_reconciled: bool
    bank_name: Optional[str] = None


def _model_to_record(model: StatementModel) -> StatementRecord:
    """Convert an ORM model to a typed Pydantic StatementRecord."""
    doc_report = DocumentTypeReport.model_validate_json(model.doc_type_report_json)
    rec_summary = ReconciliationSummary.model_validate_json(model.reconciliation_summary_json)
    stmt_meta = (
        StatementMetadata.model_validate_json(model.metadata_json)
        if model.metadata_json
        else None
    )

    transactions: List[NormalizedTransaction] = []
    for t in model.transactions:
        tx = NormalizedTransaction(
            id=t.id,
            statement_id=t.statement_id,
            line_number=t.line_number,
            page_number=t.page_number,
            date=t.date,
            date_raw=t.date_raw,
            value_date=t.value_date,
            value_date_raw=t.value_date_raw,
            description=t.description,
            description_raw=t.description_raw,
            ref_no=t.ref_no,
            channel=t.channel,
            counterparty=t.counterparty,
            debit=Decimal(t.debit) if t.debit is not None else None,
            credit=Decimal(t.credit) if t.credit is not None else None,
            amount=Decimal(t.amount) if t.amount is not None else None,
            balance=Decimal(t.balance) if t.balance is not None else None,
            currency=t.currency,
            raw_debit=t.raw_debit,
            raw_credit=t.raw_credit,
            raw_balance=t.raw_balance,
            category=t.category,
            subcategory=t.subcategory,
            category_source=ClassificationSource(t.category_source),
            category_confidence=t.category_confidence,
            rule_id=t.rule_id,
            ml_top3=json.loads(t.ml_top3_json) if t.ml_top3_json else [],
            user_edited=t.user_edited,
            flags=json.loads(t.flags_json) if t.flags_json else [],
            row_confidence=t.row_confidence,
            bounding_box=tuple(json.loads(t.bounding_box_json)),
        )
        transactions.append(tx)

    return StatementRecord(
        id=model.id,
        filename=model.filename,
        sha256=model.sha256,
        file_size_bytes=model.file_size_bytes,
        page_count=model.page_count,
        doc_type_report=doc_report,
        reconciliation_summary=rec_summary,
        transactions=transactions,
        metadata=stmt_meta,
        created_at=model.created_at,
    )


class SqliteStatementStore:
    """Production persistent SQLite statement and transaction repository."""

    def __init__(self):
        init_db()

    def save(self, record: StatementRecord) -> None:
        """Persist statement and line transactions to SQLite."""
        with SessionLocal() as session:
            # Delete any existing record with the same ID
            existing = session.get(StatementModel, record.id)
            if existing:
                session.delete(existing)
                session.flush()

            stmt_model = StatementModel(
                id=record.id,
                filename=record.filename,
                sha256=record.sha256,
                file_size_bytes=record.file_size_bytes,
                page_count=record.page_count,
                created_at=record.created_at,
                doc_type_report_json=record.doc_type_report.model_dump_json(),
                reconciliation_summary_json=record.reconciliation_summary.model_dump_json(),
                metadata_json=record.metadata.model_dump_json() if record.metadata else None,
            )

            for tx in record.transactions:
                tx_model = TransactionModel(
                    id=tx.id,
                    statement_id=record.id,
                    line_number=tx.line_number,
                    page_number=tx.page_number,
                    date=str(tx.date),
                    date_raw=tx.date_raw,
                    value_date=str(tx.value_date) if tx.value_date else None,
                    value_date_raw=tx.value_date_raw,
                    description=tx.description,
                    description_raw=tx.description_raw,
                    ref_no=tx.ref_no,
                    channel=tx.channel,
                    counterparty=tx.counterparty,
                    debit=str(tx.debit) if tx.debit is not None else None,
                    credit=str(tx.credit) if tx.credit is not None else None,
                    amount=str(tx.amount) if tx.amount is not None else None,
                    balance=str(tx.balance) if tx.balance is not None else None,
                    currency=tx.currency,
                    raw_debit=tx.raw_debit,
                    raw_credit=tx.raw_credit,
                    raw_balance=tx.raw_balance,
                    category=tx.category,
                    subcategory=tx.subcategory,
                    category_source=tx.category_source.value,
                    category_confidence=tx.category_confidence,
                    rule_id=tx.rule_id,
                    ml_top3_json=json.dumps(tx.ml_top3),
                    user_edited=tx.user_edited,
                    flags_json=json.dumps(tx.flags),
                    row_confidence=tx.row_confidence,
                    bounding_box_json=json.dumps(list(tx.bounding_box)),
                )
                stmt_model.transactions.append(tx_model)

            session.add(stmt_model)
            session.commit()

    def get(self, statement_id: str) -> Optional[StatementRecord]:
        """Fetch statement by ID including all transactions."""
        with SessionLocal() as session:
            stmt = session.get(StatementModel, statement_id)
            if not stmt:
                return None
            return _model_to_record(stmt)

    def list_all(self) -> List[StatementRecord]:
        """List all statements ordered by creation timestamp."""
        with SessionLocal() as session:
            stmts = session.scalars(
                select(StatementModel).order_by(StatementModel.created_at.desc())
            ).all()
            return [_model_to_record(s) for s in stmts]

    def list_summaries(self) -> List[StatementSummary]:
        """List lightweight summaries for history browser."""
        with SessionLocal() as session:
            stmts = session.scalars(
                select(StatementModel).order_by(StatementModel.created_at.desc())
            ).all()
            summaries: List[StatementSummary] = []
            for s in stmts:
                rec_summary = ReconciliationSummary.model_validate_json(s.reconciliation_summary_json)
                stmt_meta = (
                    StatementMetadata.model_validate_json(s.metadata_json)
                    if s.metadata_json
                    else None
                )
                summaries.append(
                    StatementSummary(
                        id=s.id,
                        filename=s.filename,
                        file_size_bytes=s.file_size_bytes,
                        page_count=s.page_count,
                        created_at=s.created_at,
                        currency=stmt_meta.currency if stmt_meta and stmt_meta.currency else "AUD",
                        transaction_count=len(s.transactions),
                        quality_score=rec_summary.quality_score,
                        statement_reconciled=rec_summary.statement_reconciled,
                        bank_name=stmt_meta.bank_name if stmt_meta else None,
                    )
                )
            return summaries

    def update_transaction(
        self, statement_id: str, transaction_id: str, new_category: str
    ) -> Optional[NormalizedTransaction]:
        """Update transaction category with manual audit trail."""
        with SessionLocal() as session:
            tx_model = session.scalars(
                select(TransactionModel).where(
                    TransactionModel.statement_id == statement_id,
                    TransactionModel.id == transaction_id,
                )
            ).first()

            if not tx_model:
                return None

            tx_model.category = new_category
            tx_model.category_source = ClassificationSource.MANUAL.value
            tx_model.category_confidence = 1.0
            tx_model.user_edited = True

            flags = json.loads(tx_model.flags_json) if tx_model.flags_json else []
            if "LOW_CONFIDENCE" in flags:
                flags.remove("LOW_CONFIDENCE")
            tx_model.flags_json = json.dumps(flags)

            session.commit()

            # Return updated Pydantic object
            return NormalizedTransaction(
                id=tx_model.id,
                statement_id=tx_model.statement_id,
                line_number=tx_model.line_number,
                page_number=tx_model.page_number,
                date=tx_model.date,
                date_raw=tx_model.date_raw,
                value_date=tx_model.value_date,
                value_date_raw=tx_model.value_date_raw,
                description=tx_model.description,
                description_raw=tx_model.description_raw,
                ref_no=tx_model.ref_no,
                channel=tx_model.channel,
                counterparty=tx_model.counterparty,
                debit=Decimal(tx_model.debit) if tx_model.debit is not None else None,
                credit=Decimal(tx_model.credit) if tx_model.credit is not None else None,
                amount=Decimal(tx_model.amount) if tx_model.amount is not None else None,
                balance=Decimal(tx_model.balance) if tx_model.balance is not None else None,
                currency=tx_model.currency,
                raw_debit=tx_model.raw_debit,
                raw_credit=tx_model.raw_credit,
                raw_balance=tx_model.raw_balance,
                category=tx_model.category,
                subcategory=tx_model.subcategory,
                category_source=ClassificationSource.MANUAL,
                category_confidence=1.0,
                rule_id=tx_model.rule_id,
                ml_top3=json.loads(tx_model.ml_top3_json) if tx_model.ml_top3_json else [],
                user_edited=True,
                flags=flags,
                row_confidence=tx_model.row_confidence,
                bounding_box=tuple(json.loads(tx_model.bounding_box_json)),
            )

    def delete(self, statement_id: str) -> bool:
        """Delete statement and cascade to all its transactions."""
        with SessionLocal() as session:
            stmt = session.get(StatementModel, statement_id)
            if not stmt:
                return False
            session.delete(stmt)
            session.commit()
            return True


# Global persistent storage singleton
statement_store = SqliteStatementStore()
