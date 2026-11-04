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

    # Rent & Housing (debit)
    ("RENT PAYMENT HARBOUR PROPERTY", "Rent & Housing", "debit"),
    ("RESIDENTIAL LEASE RENT PAYMENT", "Rent & Housing", "debit"),
    ("MORTGAGE REPAYMENT HOME LOAN", "Rent & Housing", "debit"),
    ("BODY CORPORATE STRATA LEVY", "Rent & Housing", "debit"),
    ("REAL ESTATE RENT DIRECT DEBIT", "Rent & Housing", "debit"),

    # Transfers In (credit)
    ("PAYID TRANSFER RECEIVED FROM TONY", "Transfers In", "credit"),
    ("OSKO PAYMENT RECEIVED SETTLEMENT", "Transfers In", "credit"),
    ("TRANSFER FROM SAVINGS ACCOUNT", "Transfers In", "credit"),
    ("DIRECT CREDIT P2P TRANSFER", "Transfers In", "credit"),

    # Transfers Out (debit)
    ("TRANSFER TO SAVINGS MONTHLY", "Transfers Out", "debit"),
    ("OSKO TRANSFER TO EMILY", "Transfers Out", "debit"),
    ("NETBANK INTERNAL TRANSFER", "Transfers Out", "debit"),
    ("TRANSFER TO INVESTMENT SAVER", "Transfers Out", "debit"),

    # Refunds & Cashbacks (credit)
    ("REFUND RETAIL PURCHASE AMAZON", "Refunds & Cashbacks", "credit"),
    ("MERCHANT REFUND REVERSAL TARGET", "Refunds & Cashbacks", "credit"),
    ("CASHBACK REBATE PROMOTION", "Refunds & Cashbacks", "credit"),
    ("CARD PURCHASE REFUND STORE", "Refunds & Cashbacks", "credit"),

    # Insurance (debit)
    ("INSURANCE PREMIUM MONTHLY CHARGE", "Insurance", "debit"),
    ("BUPA HEALTH INSURANCE PREMIUM", "Insurance", "debit"),
    ("MEDIBANK PRIVATE HEALTH D/D", "Insurance", "debit"),
    ("ALLIANZ CAR INSURANCE ANNUAL", "Insurance", "debit"),
    ("NRMA COMPREHENSIVE INSURANCE", "Insurance", "debit"),
    ("AAMI HOME AND CONTENTS POLICY", "Insurance", "debit"),

    # Merchants & Lines from Synthetic Dataset (Global / US / AU / UK)
    ("TACO BELL FAST FOOD", "Dining & Restaurants", "debit"),
    ("CHIPOTLE MEXICAN GRILL", "Dining & Restaurants", "debit"),
    ("BURGER KING MEAL", "Dining & Restaurants", "debit"),
    ("PANERA BREAD BAKERY", "Dining & Restaurants", "debit"),
    ("APPLEBEES NEIGHBORHOOD GRILL", "Dining & Restaurants", "debit"),
    ("STEAM ONLINE GAME STORE", "Entertainment & Subscriptions", "debit"),
    ("HULU MONTHLY SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),
    ("HBO MAX STREAMING SERVICE", "Entertainment & Subscriptions", "debit"),
    ("NINTENDO ESHOP DIGITAL", "Entertainment & Subscriptions", "debit"),
    ("PLAYSTATION NETWORK STORE", "Entertainment & Subscriptions", "debit"),
    ("TRADER JOES GROCERY STORE", "Groceries", "debit"),
    ("WHOLE FOODS ORGANIC MARKET", "Groceries", "debit"),
    ("SAFEWAY SUPERMARKET FOOD", "Groceries", "debit"),
    ("KROGER FRESH GROCERIES", "Groceries", "debit"),
    ("EXXON MOBIL GAS STATION", "Transport & Travel", "debit"),
    ("CHEVRON FUEL STOP PETROL", "Transport & Travel", "debit"),
    ("HIGHWAY GAS STOP DIESEL", "Transport & Travel", "debit"),
    ("LOCAL GAS STATION SERVO", "Transport & Travel", "debit"),
    ("CARD PURCHASE FUEL STATION", "Transport & Travel", "debit"),
    ("OPAL TOP UP TRANSPORT SYDNEY", "Transport & Travel", "debit"),
    ("CVS PHARMACY HEALTH STORE", "Healthcare & Pharmacy", "debit"),
    ("WALGREENS HEALTH AND DRUGS", "Healthcare & Pharmacy", "debit"),
    ("RITE AID PRESCRIPTION PHARMACY", "Healthcare & Pharmacy", "debit"),
    ("LOCAL HOSPITAL URGENT CARE", "Healthcare & Pharmacy", "debit"),
    ("MEDICARE REBATE DIRECT CREDIT", "Healthcare & Pharmacy", "credit"),
    ("AIRBNB RESERVATION BOOKING", "Transport & Travel", "debit"),
    ("DELTA AIRLINES FLIGHT TICKET", "Transport & Travel", "debit"),
    ("AMERICAN AIRLINES BOOKING", "Transport & Travel", "debit"),
    ("HERTZ CAR RENTAL AIRPORT", "Transport & Travel", "debit"),
    ("ENTERPRISE RENT-A-CAR HIRE", "Transport & Travel", "debit"),
    ("HILTON HOTEL STAY LODGING", "Transport & Travel", "debit"),
    ("HOME DEPOT HARDWARE SUPPLIES", "Shopping & Retail", "debit"),
    ("IKEA FURNITURE HOME STORE", "Shopping & Retail", "debit"),
    ("COSTCO WHOLESALE WAREHOUSE", "Shopping & Retail", "debit"),
    ("TARGET DEPARTMENT STORE RETAIL", "Shopping & Retail", "debit"),
    ("WALMART SUPERCENTER PURCHASE", "Shopping & Retail", "debit"),
    ("ETSY CRAFTS ONLINE MARKET", "Shopping & Retail", "debit"),
    ("NIKE STORE SPORTS RETAIL", "Shopping & Retail", "debit"),
    ("SEPHORA BEAUTY STORE", "Shopping & Retail", "debit"),
    ("COURSERA ONLINE LEARNING", "Shopping & Retail", "debit"),
    ("UDEMY ONLINE COURSE EDUCATION", "Shopping & Retail", "debit"),
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
