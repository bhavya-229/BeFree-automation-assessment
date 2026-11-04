"""SQLite database engine, connection pragmas, and SQLAlchemy 2 ORM models."""

import json
import os
from pathlib import Path
from typing import Any, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


# Support cross-platform storage path (Windows local or Linux Docker container)
env_data_dir = os.environ.get("DATA_DIR")
if env_data_dir:
    DB_PATH = Path(env_data_dir) / "statements.db"
else:
    # Resolve relative to backend directory or working directory
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    candidate = base_dir / "data" / "statements.db"
    if candidate.parent.exists():
        DB_PATH = candidate
    else:
        DB_PATH = Path("data/statements.db").resolve()

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@event.listens_for(engine, "connect")
def configure_sqlite_pragmas(dbapi_connection, connection_record):
    """Enable Write-Ahead Logging (WAL) and foreign keys with fallback for Docker volume mounts."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
    except Exception:
        # Fallback to DELETE mode on virtual volume mounts (e.g. Windows NTFS mounted into Linux Docker)
        cursor.execute("PRAGMA journal_mode=DELETE")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class StatementModel(Base):
    """Persisted bank statement header & provenance record."""

    __tablename__ = "statements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)

    # Serialized JSON structures
    doc_type_report_json: Mapped[str] = mapped_column(Text, nullable=False)
    reconciliation_summary_json: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    transactions: Mapped[List["TransactionModel"]] = relationship(
        "TransactionModel",
        back_populates="statement",
        cascade="all, delete-orphan",
        order_by="TransactionModel.line_number",
    )


class TransactionModel(Base):
    """Persisted line transaction record."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    statement_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("statements.id", ondelete="CASCADE"), index=True, nullable=False
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)

    date: Mapped[str] = mapped_column(String(20), nullable=False)
    date_raw: Mapped[str] = mapped_column(String(50), nullable=False)
    value_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    value_date_raw: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_raw: Mapped[str] = mapped_column(Text, nullable=False)
    ref_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    channel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    counterparty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Decimal representations stored as strings
    debit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    credit: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    amount: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    balance: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="AUD")

    raw_debit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_credit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_balance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category_source: Mapped[str] = mapped_column(String(20), nullable=False)
    category_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    rule_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ml_top3_json: Mapped[str] = mapped_column(Text, default="[]")

    user_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    flags_json: Mapped[str] = mapped_column(Text, default="[]")
    row_confidence: Mapped[float] = mapped_column(Float, default=100.0)
    bounding_box_json: Mapped[str] = mapped_column(Text, default="[0, 0, 0, 0]")

    statement: Mapped["StatementModel"] = relationship("StatementModel", back_populates="transactions")


class UserRuleModel(Base):
    """Persisted user correction rules for active learning across statements."""

    __tablename__ = "user_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str] = mapped_column(String(50), nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=1)


def init_db() -> None:
    """Initialize SQLite tables."""
    Base.metadata.create_all(bind=engine)
