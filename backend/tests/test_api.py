"""End-to-end integration tests for FastAPI statements, review, and export endpoints."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Verify health endpoint responds with status ok."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_statement_api_workflow(client, sample_digital_pdf: Path):
    """Verify complete API workflow: upload -> list -> correct category -> export CSV & XLSX."""
    # 1. Upload & Process Statement
    with open(sample_digital_pdf, "rb") as f:
        upload_resp = client.post(
            "/api/v1/statements",
            files={"file": ("cba_statement.pdf", f, "application/pdf")},
        )

    assert upload_resp.status_code == 201
    data = upload_resp.json()
    statement_id = data["id"]
    assert data["filename"] == "cba_statement.pdf"
    assert data["doc_type_report"]["doc_type"] == "DIGITAL"
    assert len(data["transactions"]) == 3

    # Check Woolworths transaction classified as Groceries by Rule
    woolworths_txn = data["transactions"][0]
    assert "WOOLWORTHS" in woolworths_txn["description"]
    assert woolworths_txn["category"] == "Groceries"
    assert woolworths_txn["category_source"] == "RULE"

    # 2. Search / Filter transactions
    filter_resp = client.get(
        f"/api/v1/statements/{statement_id}/transactions",
        params={"q": "TELSTRA"},
    )
    assert filter_resp.status_code == 200
    filtered_data = filter_resp.json()
    assert filtered_data["total"] == 1
    assert "TELSTRA" in filtered_data["transactions"][0]["description"]

    # 3. Manual category correction
    txn_id_to_edit = woolworths_txn["id"]
    patch_resp = client.patch(
        f"/api/v1/statements/{statement_id}/transactions/{txn_id_to_edit}",
        json={"category": "Dining & Restaurants"},
    )
    assert patch_resp.status_code == 200
    patched_data = patch_resp.json()
    assert patched_data["category"] == "Dining & Restaurants"
    assert patched_data["category_source"] == "MANUAL"
    assert patched_data["user_edited"] is True

    # 4. Export CSV
    csv_resp = client.get(f"/api/v1/statements/{statement_id}/export/csv")
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert csv_resp.content.startswith(b"\xef\xbb\xbf")
    assert b"Dining & Restaurants" in csv_resp.content

    # 5. Export Excel (.xlsx)
    xlsx_resp = client.get(f"/api/v1/statements/{statement_id}/export/xlsx")
    assert xlsx_resp.status_code == 200
    assert "openxmlformats" in xlsx_resp.headers["content-type"]
    assert len(xlsx_resp.content) > 1000


def test_encrypted_pdf_handling(client):
    """Verify password-protected PDF lifecycle: 401 PDF_ENCRYPTED -> 401 WRONG_PASSWORD -> 200 success."""
    # 1. Calling encrypted endpoint without password returns 401 PDF_ENCRYPTED
    resp1 = client.post("/api/v1/statements/samples/encrypted")
    assert resp1.status_code == 401
    err1 = resp1.json()["detail"]
    assert err1["code"] == "PDF_ENCRYPTED"

    # 2. Calling with wrong password returns 401 WRONG_PASSWORD
    resp2 = client.post("/api/v1/statements/samples/encrypted?password=incorrect")
    assert resp2.status_code == 401
    err2 = resp2.json()["detail"]
    assert err2["code"] == "WRONG_PASSWORD"

    # 3. Calling with valid password decrypts in-memory and succeeds
    resp3 = client.post("/api/v1/statements/samples/encrypted?password=befree2026")
    assert resp3.status_code == 201
    data3 = resp3.json()
    assert data3["filename"] == "Protected_CBA_Statement.pdf"
    assert len(data3["transactions"]) == 10
    assert data3["reconciliation_summary"]["reconciled_count"] == 10
    assert data3["reconciliation_summary"]["quality_score"] == 100.0
