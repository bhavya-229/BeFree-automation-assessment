"""Generate synthetic sample statements for Australian, UK, and Indian banks."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def make_cba_statement(output_path: Path) -> None:
    """Generate a clean Australian Commonwealth Bank (CBA) statement."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.drawString(50, 750, "Commonwealth Bank of Australia - Statement of Account")
    c.drawString(50, 730, "Account: 062-000 12345678    Currency: AUD")
    c.drawString(50, 715, "Period: 01 Oct 2023 to 31 Oct 2023")

    # Table Header
    c.drawString(50, 680, "Date")
    c.drawString(130, 680, "Description")
    c.drawString(330, 680, "Debit")
    c.drawString(410, 680, "Credit")
    c.drawString(490, 680, "Balance")

    # Opening balance
    c.drawString(50, 650, "01/10/2023")
    c.drawString(130, 650, "Opening Balance")
    c.drawString(490, 650, "2,450.00")

    # Transactions
    rows = [
        ("02/10/2023", "WOOLWORTHS METRO SYDNEY", "74.20", "", "2,375.80"),
        ("05/10/2023", "SALARY DIRECT CREDIT TECH CORP", "", "3,450.00", "5,825.80"),
        ("08/10/2023", "TELSTRA BILL PAYMENT D/D", "110.00", "", "5,715.80"),
        ("12/10/2023", "BUNNINGS WAREHOUSE HARDWARE", "185.40", "", "5,530.40"),
        ("15/10/2023", "COLES SUPERMARKET CHATSWOOD", "92.30", "", "5,438.10"),
        ("18/10/2023", "LINKT TOLL SYDNEY MOTORWAYS", "34.50", "", "5,403.60"),
        ("22/10/2023", "NETFLIX AUSTRALIA SUBSCRIPTION", "22.99", "", "5,380.61"),
        ("25/10/2023", "CHEMIST WAREHOUSE GEORGE ST", "48.60", "", "5,332.01"),
        ("28/10/2023", "ATM CASH WITHDRAWAL GEORGE ST", "200.00", "", "5,132.01"),
        ("31/10/2023", "SAVINGS REWARD INTEREST PAID", "", "15.40", "5,147.41"),
    ]

    y = 620
    for dt, desc, deb, cred, bal in rows:
        c.drawString(50, y, dt)
        c.drawString(130, y, desc)
        if deb:
            c.drawString(330, y, deb)
        if cred:
            c.drawString(410, y, cred)
        c.drawString(490, y, bal)
        y -= 25

    c.drawString(50, y - 20, "Closing Balance as at 31/10/2023: $5,147.41")
    c.save()


def make_barclays_statement(output_path: Path) -> None:
    """Generate a clean UK Barclays statement."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(45, 750, "Barclays Bank UK PLC - Your Bank Statement")
    c.setFont("Helvetica", 9)
    c.drawString(45, 730, "Sort Code: 20-00-00   Account Number: 87654321   Currency: GBP")
    c.drawString(45, 715, "Statement Date: 31 October 2023")

    # Table Header
    c.setFont("Helvetica-Bold", 9)
    c.drawString(45, 680, "Date")
    c.drawString(125, 680, "Description")
    c.drawString(340, 680, "Money Out")
    c.drawString(425, 680, "Money In")
    c.drawString(500, 680, "Balance")

    # Transactions
    rows = [
        ("02 Oct 2023", "TESCO STORES LONDON", "32.40", "", "1,250.00"),
        ("04 Oct 2023", "TRANSPORT FOR LONDON CONTACTLESS", "7.80", "", "1,242.20"),
        ("07 Oct 2023", "EMPLOYER SALARY BACS", "", "2,800.00", "4,042.20"),
        ("10 Oct 2023", "BRITISH GAS MONTHLY DIRECT DEBIT", "85.00", "", "3,957.20"),
        ("14 Oct 2023", "PRET A MANGER VICTORIA", "9.50", "", "3,947.70"),
        ("18 Oct 2023", "SAINSBURYS SUPERMARKET", "54.20", "", "3,893.50"),
        ("22 Oct 2023", "SPOTIFY UK SUBSCRIPTION", "10.99", "", "3,882.51"),
        ("26 Oct 2023", "BOOTS THE CHEMIST PICCADILLY", "18.30", "", "3,864.21"),
    ]

    y = 650
    c.setFont("Helvetica", 9)
    for dt, desc, deb, cred, bal in rows:
        c.drawString(45, y, dt)
        c.drawString(125, y, desc)
        if deb:
            c.drawString(340, y, deb)
        if cred:
            c.drawString(425, y, cred)
        c.drawString(500, y, bal)
        y -= 25

    c.save()


def make_westpac_statement(output_path: Path) -> None:
    """Generate a clean Australian Westpac statement."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.drawString(50, 750, "Westpac Banking Corporation - Account Statement")
    c.drawString(50, 730, "BSB: 032-000    Account No: 98765432    Currency: AUD")
    c.drawString(50, 715, "Statement Period: 01 Nov 2023 to 30 Nov 2023")

    c.drawString(50, 680, "Date")
    c.drawString(130, 680, "Transaction Details")
    c.drawString(330, 680, "Withdrawals")
    c.drawString(410, 680, "Deposits")
    c.drawString(490, 680, "Balance")

    rows = [
        ("01/11/2023", "OPENING BALANCE BROUGHT FORWARD", "", "", "3,120.00"),
        ("03/11/2023", "UBER RIDES SYDNEY NSW", "28.50", "", "3,091.50"),
        ("07/11/2023", "FORTNIGHTLY SALARY XYZ TECH", "", "2,950.00", "6,041.50"),
        ("11/11/2023", "ENERGYAUSTRALIA DIRECT DEBIT", "142.80", "", "5,898.70"),
        ("15/11/2023", "ALDI SUPERMARKET BROADWAY", "65.40", "", "5,833.30"),
        ("20/11/2023", "JB HI-FI SYDNEY CITY", "129.00", "", "5,704.30"),
        ("24/11/2023", "MONTHLY ACCOUNT MAINTENANCE FEE", "5.00", "", "5,699.30"),
        ("28/11/2023", "TRANSFER IN FROM JOHN DOE", "", "150.00", "5,849.30"),
    ]

    y = 650
    for dt, desc, deb, cred, bal in rows:
        c.drawString(50, y, dt)
        c.drawString(130, y, desc)
        if deb:
            c.drawString(330, y, deb)
        if cred:
            c.drawString(410, y, cred)
        c.drawString(490, y, bal)
        y -= 25

    c.drawString(50, y - 20, "Closing Balance: $5,849.30")
    c.save()


def make_encrypted_cba_statement(output_path: Path, password: str = "befree2026") -> None:
    """Generate a password-protected encrypted statement using pikepdf."""
    import pikepdf
    # First generate clean temp statement
    temp_path = output_path.with_suffix(".tmp.pdf")
    make_cba_statement(temp_path)

    # Encrypt with 256-bit AES
    with pikepdf.Pdf.open(temp_path) as pdf:
        enc = pikepdf.Encryption(owner="admin_owner", user=password, R=6)
        pdf.save(output_path, encryption=enc)

    if temp_path.exists():
        temp_path.unlink()


def make_sbi_statement(output_path: Path) -> None:
    """Generate a clean Indian State Bank of India (SBI) statement."""
    c = canvas.Canvas(str(output_path), pagesize=letter)
    c.drawString(50, 750, "State Bank of India - Account Statement")
    c.drawString(50, 730, "IFSC: SBIN0001234    Account: 20491823901    Currency: INR")
    c.drawString(50, 715, "Period: 01 Oct 2023 to 31 Oct 2023")

    c.drawString(50, 680, "Txn Date")
    c.drawString(130, 680, "Narration")
    c.drawString(330, 680, "Debit")
    c.drawString(410, 680, "Credit")
    c.drawString(490, 680, "Balance")

    rows = [
        ("02-10-2023", "SWIGGY BANGALORE UPI 3291823019", "450.00", "", "45,200.00"),
        ("05-10-2023", "MONTHLY SALARY CREDITED BY INFOSYS", "", "65,000.00", "1,10,200.00"),
        ("10-10-2023", "BESCOM ELECTRICITY BILL NACH", "1,850.00", "", "1,08,350.00"),
        ("15-10-2023", "AMAZON INDIA PAY ONLINE", "2,340.00", "", "1,06,010.00"),
        ("22-10-2023", "APOLLO PHARMACY BANGALORE", "680.00", "", "1,05,330.00"),
        ("28-10-2023", "ATM CASH WDL MG ROAD", "5,000.00", "", "1,00,330.00"),
    ]

    y = 650
    for dt, desc, deb, cred, bal in rows:
        c.drawString(50, y, dt)
        c.drawString(130, y, desc)
        if deb:
            c.drawString(330, y, deb)
        if cred:
            c.drawString(410, y, cred)
        c.drawString(490, y, bal)
        y -= 25

    c.save()


def main():
    samples_dir = Path("d:/beFree/data/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)

    make_cba_statement(samples_dir / "cba_australian_statement.pdf")
    make_barclays_statement(samples_dir / "barclays_uk_statement.pdf")
    make_westpac_statement(samples_dir / "westpac_australian_statement.pdf")
    make_sbi_statement(samples_dir / "sbi_india_statement.pdf")
    make_encrypted_cba_statement(samples_dir / "encrypted_cba_statement.pdf")
    print("Generated all 5 bank sample fixtures in d:/beFree/data/samples/")


if __name__ == "__main__":
    main()
