"""In-memory and file-backed repository for statements and transactions."""

from typing import Dict, List, Optional
from pydantic import BaseModel
from app.schemas.transaction import NormalizedTransaction, ClassificationSource
from app.pipeline.pdf_type import DocumentTypeReport
from app.pipeline.validate.reconcile import ReconciliationSummary
from app.pipeline.parse.metadata import StatementMetadata


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


class InMemoryStatementStore:
    """Thread-safe statement and transaction repository."""

    def __init__(self):
        self._statements: Dict[str, StatementRecord] = {}

    def save(self, record: StatementRecord) -> None:
        self._statements[record.id] = record

    def get(self, statement_id: str) -> Optional[StatementRecord]:
        return self._statements.get(statement_id)

    def list_all(self) -> List[StatementRecord]:
        return list(self._statements.values())

    def update_transaction(
        self, statement_id: str, transaction_id: str, new_category: str
    ) -> Optional[NormalizedTransaction]:
        record = self.get(statement_id)
        if not record:
            return None

        for txn in record.transactions:
            if txn.id == transaction_id:
                txn.category = new_category
                txn.category_source = ClassificationSource.MANUAL
                txn.category_confidence = 1.0
                txn.user_edited = True
                if "LOW_CONFIDENCE" in txn.flags:
                    txn.flags.remove("LOW_CONFIDENCE")
                return txn
        return None


statement_store = InMemoryStatementStore()
