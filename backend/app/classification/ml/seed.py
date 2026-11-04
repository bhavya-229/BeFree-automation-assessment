"""Synthetic training seeds and isolated held-out evaluation sets."""

from typing import List, Tuple

# Training set: realistic AU/UK/Universal transactions with varied rails and narrations
TRAINING_SAMPLES: List[Tuple[str, str, str]] = [
    # Salary & Wages (credit)
    ("SALARY DIRECT CREDIT ACME CORP", "Salary & Wages", "credit"),
    ("PAYROLL BACS TRANSMISSION MONTHLY", "Salary & Wages", "credit"),
    ("WAGES PAYMENT TECH PTY LTD", "Salary & Wages", "credit"),
    ("DIRECT CREDIT PAYROLL SERVICES", "Salary & Wages", "credit"),
    ("FORTNIGHTLY SALARY DEPOSIT", "Salary & Wages", "credit"),

    # Groceries (debit)
    ("WOOLWORTHS METRO SURRY HILLS SYDNEY", "Groceries", "debit"),
    ("COLES SUPERMARKETS CHATSWOOD", "Groceries", "debit"),
    ("ALDI STORES BURWOOD", "Groceries", "debit"),
    ("TESCO EXPRESS REGENT STREET LONDON", "Groceries", "debit"),
    ("SAINSBURYS S/MKTS CAMDEN", "Groceries", "debit"),
    ("ASDA SUPERSTORE MANCHESTER", "Groceries", "debit"),
    ("WAITROSE EDINBURGH FOOD", "Groceries", "debit"),
    ("LIDL UK BARKING GROCERY", "Groceries", "debit"),

    # Utilities & Bills (debit)
    ("TELSTRA TELECOM BILL PAYMENT", "Utilities & Bills", "debit"),
    ("OPTUS MOBILE MONTHLY CHARGES", "Utilities & Bills", "debit"),
    ("AGL ELECTRICITY DIRECT DEBIT", "Utilities & Bills", "debit"),
    ("ORIGIN ENERGY NATURAL GAS", "Utilities & Bills", "debit"),
    ("SYDNEY WATER RATES PAYMENT", "Utilities & Bills", "debit"),
    ("BRITISH GAS MONTHLY BILL DIRECT DEBIT", "Utilities & Bills", "debit"),
    ("EDF ENERGY QUARTERLY D/D", "Utilities & Bills", "debit"),
    ("THAMES WATER UTILITIES DIRECT DEBIT", "Utilities & Bills", "debit"),
    ("EE MOBILE CONTRACT PAYMENT", "Utilities & Bills", "debit"),
    ("BT BROADBAND SERVICES BILL", "Utilities & Bills", "debit"),

    # Transport & Travel (debit)
    ("TRANSPORT FOR LONDON TFL TRAVEL CONTACTLESS", "Transport & Travel", "debit"),
    ("TFL.GOV.UK UNDERGROUND FARE", "Transport & Travel", "debit"),
    ("NATIONAL RAIL TICKET OFFICE PADDINGTON", "Transport & Travel", "debit"),
    ("LINKT TOLL PAYMENT SYDNEY MOTORWAYS", "Transport & Travel", "debit"),
    ("TRANSURBAN TOLLWAY CHARGE", "Transport & Travel", "debit"),
    ("AMPOL SERVICE STATION FUEL", "Transport & Travel", "debit"),
    ("BP CONNECT SERVICE STATION PETROL", "Transport & Travel", "debit"),
    ("UBER *TRIP RIDESHARE SYDNEY", "Transport & Travel", "debit"),
    ("UBER TRIP PENDING RIDE LONDON", "Transport & Travel", "debit"),

    # Dining & Restaurants (debit)
    ("STARBUCKS COFFEE PADDINGTON", "Dining & Restaurants", "debit"),
    ("COSTA COFFEE HIGH STREET", "Dining & Restaurants", "debit"),
    ("PRET A MANGER VICTORIA STATION", "Dining & Restaurants", "debit"),
    ("GREGGS BAKERY LUNCH", "Dining & Restaurants", "debit"),
    ("MCDONALDS RESTAURANT GEORGE ST", "Dining & Restaurants", "debit"),
    ("HUNGRY JACKS FAST FOOD", "Dining & Restaurants", "debit"),
    ("UBER EATS ONLINE FOOD ORDER", "Dining & Restaurants", "debit"),
    ("DELIVEROO MEAL DELIVERY", "Dining & Restaurants", "debit"),

    # Shopping & Retail (debit)
    ("BUNNINGS WAREHOUSE HARDWARE", "Shopping & Retail", "debit"),
    ("KMART BROADWAY RETAIL STORE", "Shopping & Retail", "debit"),
    ("JB HI-FI ELECTRONICS STRATHFIELD", "Shopping & Retail", "debit"),
    ("AMAZON AU MARKETPLACE PURCHASE", "Shopping & Retail", "debit"),
    ("AMAZON UK RETAIL ONLINE", "Shopping & Retail", "debit"),
    ("MARKS AND SPENCER OXFORD ST", "Shopping & Retail", "debit"),
    ("PRIMARK CLOTHING STORE", "Shopping & Retail", "debit"),
    ("ARGOS RETAIL ONLINE LTD", "Shopping & Retail", "debit"),

    # Healthcare & Pharmacy (debit)
    ("CHEMIST WAREHOUSE GEORGE ST PHARMACY", "Healthcare & Pharmacy", "debit"),
    ("PRICELINE PHARMACY BONDI", "Healthcare & Pharmacy", "debit"),
    ("BOOTS THE CHEMIST PICCADILLY", "Healthcare & Pharmacy", "debit"),
    ("SUPERDRUG HEALTHCARE LONDON", "Healthcare & Pharmacy", "debit"),
    ("SYDNEY MEDICAL CENTRE CONSULT", "Healthcare & Pharmacy", "debit"),

    # Entertainment & Subscriptions (debit)
    ("NETFLIX STREAMING SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),
    ("SPOTIFY PREMIUM MONTHLY MUSIC", "Entertainment & Subscriptions", "debit"),
    ("DISNEY PLUS DIGITAL MEDIA", "Entertainment & Subscriptions", "debit"),
    ("YOUTUBE PREMIUM GOOGLE SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),
    ("APPLE.COM/BILL DIGITAL SUBSCRIPTIONS", "Entertainment & Subscriptions", "debit"),

    # Bank Fees (debit)
    ("MONTHLY ACCOUNT SERVICE FEE", "Fees & Charges", "debit"),
    ("OVERDRAWN ACCOUNT CHARGE", "Fees & Charges", "debit"),
    ("INTERNATIONAL TRANSACTION FEE", "Fees & Charges", "debit"),
    ("ATM NON-NETWORK WITHDRAWAL FEE", "Fees & Charges", "debit"),

    # Cash Withdrawal (debit)
    ("ATM CASH WITHDRAWAL GEORGE ST", "Cash Withdrawal", "debit"),
    ("ATM WDL BRANCH CASHOUT", "Cash Withdrawal", "debit"),
    ("BRANCH CASH WITHDRAWAL OVER COUNTER", "Cash Withdrawal", "debit"),

    # Interest Earned (credit)
    ("CREDIT INTEREST PAID", "Interest & Investments", "credit"),
    ("INTEREST EARNED SAVER ACCOUNT", "Interest & Investments", "credit"),
]


# Held-out evaluation set: UNSEEN merchants and narrations not present in training or rule keywords!
HELD_OUT_TEST_SAMPLES: List[Tuple[str, str, str]] = [
    # Salary
    ("DIRECT CR TECHSTAFF PAY OCTOBER", "Salary & Wages", "credit"),
    ("BACS TRANSFER EMPLOYEE REMUNERATION", "Salary & Wages", "credit"),

    # Groceries (unseen brands/stores)
    ("BOOTH'S FOODSTORE GROCERY", "Groceries", "debit"),
    ("SPAR SUPERMARKET CONVENIENCE", "Groceries", "debit"),

    # Utilities
    ("WATERLOO WATER SERVICE CHARGES", "Utilities & Bills", "debit"),
    ("POWERGRID ELECTRICITY BILL", "Utilities & Bills", "debit"),

    # Transport
    ("SOUTHERN RAILWAY TICKET FARE", "Transport & Travel", "debit"),
    ("SHELL PETROLEUM SERVICE FILL", "Transport & Travel", "debit"),

    # Dining
    ("CAFE NERO ESPRESSO LUNCH", "Dining & Restaurants", "debit"),
    ("LEON RESTAURANT HEALTHY FAST FOOD", "Dining & Restaurants", "debit"),

    # Shopping
    ("CURRYS PC WORLD ELECTRONICS", "Shopping & Retail", "debit"),
    ("SELFRIDGES DEPARTMENT STORE", "Shopping & Retail", "debit"),

    # Healthcare
    ("CITY DENTAL SURGERY CHECKUP", "Healthcare & Pharmacy", "debit"),
    ("MEDICARE CLINIC HEALTH VISIT", "Healthcare & Pharmacy", "debit"),

    # Entertainment
    ("CRUNCHYROLL ANIME STREAMING", "Entertainment & Subscriptions", "debit"),
    ("PARAMOUNT PLUS SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),

    # Fees
    ("UNAUTHORISED OVERDRAFT CHARGE", "Fees & Charges", "debit"),

    # Cash
    ("CASH DISPENSE HIGH STREET MACHINE", "Cash Withdrawal", "debit"),
]
