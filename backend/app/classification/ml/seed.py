"""Synthetic training seeds and isolated held-out evaluation sets."""

from typing import List, Tuple

# Comprehensive multi-region training set covering AU, UK, India, and Universal banking rails across all 24 categories.
TRAINING_SAMPLES: List[Tuple[str, str, str]] = [
    # 1. Salary & Wages (credit)
    ("SALARY DIRECT CREDIT ACME CORP", "Salary & Wages", "credit"),
    ("PAYROLL BACS TRANSMISSION MONTHLY", "Salary & Wages", "credit"),
    ("WAGES PAYMENT TECH PTY LTD", "Salary & Wages", "credit"),
    ("DIRECT CREDIT PAYROLL SERVICES", "Salary & Wages", "credit"),
    ("FORTNIGHTLY SALARY DEPOSIT", "Salary & Wages", "credit"),
    ("MONTHLY SALARY CREDIT TATA CONSULTANCY", "Salary & Wages", "credit"),
    ("INFOSYS BPO PAYROLL DIRECT CR", "Salary & Wages", "credit"),
    ("ACCENTURE SERVICES SALARY CR", "Salary & Wages", "credit"),
    ("NHS HOSPITAL PAYROLL DIRECT CREDIT", "Salary & Wages", "credit"),
    ("GOVERNMENT DEPARTMENT PAYROLL REMUNERATION", "Salary & Wages", "credit"),
    ("FORTNIGHTLY WAGES TRANSFER TECH CORP", "Salary & Wages", "credit"),

    # 2. Transfers In (credit)
    ("PAYID TRANSFER RECEIVED JOHN DOE", "Transfers In", "credit"),
    ("OSKO PAYMENT RECEIVED FROM JANE", "Transfers In", "credit"),
    ("DIRECT CREDIT TRANSFER FROM SAVINGS", "Transfers In", "credit"),
    ("UPI/621671144280/CR/CHHELA/BARB/rajuchela/UPI", "Transfers In", "credit"),
    ("UPI/658261158882/CR/SACHIN/SBIN/sachincha/UPI", "Transfers In", "credit"),
    ("IMPS/CR/123456789/FRIEND/HDFC", "Transfers In", "credit"),
    ("NEFT/CR/BARB0001/FAMILY TRANSFER", "Transfers In", "credit"),
    ("FASTER PAYMENTS INCOMING MR SMITH", "Transfers In", "credit"),
    ("BACS CREDIT TRANSFER FROM ACCOUNT", "Transfers In", "credit"),
    ("P2P MONEY RECEIVED FROM PEER", "Transfers In", "credit"),
    ("DEPOSIT TRANSFER IN FROM EXTERNAL ACCOUNT", "Transfers In", "credit"),

    # 3. Interest & Investments (credit)
    ("INTEREST PAID ON SAVINGS ACCOUNT", "Interest & Investments", "credit"),
    ("CREDIT INTEREST APPLIED", "Interest & Investments", "credit"),
    ("QUARTERLY BANK INTEREST EARNED", "Interest & Investments", "credit"),
    ("VANGUARD DIVIDEND PAYMENT CR", "Interest & Investments", "credit"),
    ("COMMSEC DIVIDEND REINVESTMENT CR", "Interest & Investments", "credit"),
    ("BHP GROUP DIVIDEND DIRECT CREDIT", "Interest & Investments", "credit"),
    ("FIXED DEPOSIT MATURITY INTEREST CR", "Interest & Investments", "credit"),
    ("TERM DEPOSIT MONTHLY INTEREST DEPOSIT", "Interest & Investments", "credit"),
    ("DIVIDEND PAYMENT AUSTRALIAN EQUITIES", "Interest & Investments", "credit"),

    # 4. Refunds & Cashbacks (credit)
    ("REFUND - RETAIL PURCHASE ASOS", "Refunds & Cashbacks", "credit"),
    ("MERCHANT REFUND - AMAZON UK", "Refunds & Cashbacks", "credit"),
    ("CASHBACK REWARD BANK PROMO", "Refunds & Cashbacks", "credit"),
    ("PURCHASE REVERSAL WOOLWORTHS", "Refunds & Cashbacks", "credit"),
    ("UPI/622330342177/CR/Flipka/YESB/flipkart./Refund", "Refunds & Cashbacks", "credit"),
    ("FLIPKART RETURN REFUND PROCESSED", "Refunds & Cashbacks", "credit"),
    ("EBAY DISPUTE RESOLUTION REFUND", "Refunds & Cashbacks", "credit"),
    ("AIRBNB TRIP CANCELLATION REFUND CR", "Refunds & Cashbacks", "credit"),
    ("RETAIL RETURN MERCHANT RECREDIT", "Refunds & Cashbacks", "credit"),

    # 5. Other Income (credit)
    ("FREELANCE CONSULTING INVOICE PAYMENT", "Other Income", "credit"),
    ("UPWORK ESCROW PAYOUT DIRECT CR", "Other Income", "credit"),
    ("GUMTREE PRIVATE SALE CASH DEPOSIT", "Other Income", "credit"),
    ("AIRTASKER TASK PAYMENT CR", "Other Income", "credit"),
    ("FIVERR REVENUE WITHDRAWAL CREDIT", "Other Income", "credit"),
    ("CASH DEPOSIT AT BRANCH COUNTER", "Other Income", "credit"),
    ("PRIVATE CONSULTING HONORARIUM", "Other Income", "credit"),

    # 6. Groceries (debit)
    ("WOOLWORTHS METRO SURRY HILLS SYDNEY", "Groceries", "debit"),
    ("COLES SUPERMARKETS CHATSWOOD", "Groceries", "debit"),
    ("ALDI STORES BURWOOD", "Groceries", "debit"),
    ("TESCO EXPRESS REGENT STREET LONDON", "Groceries", "debit"),
    ("SAINSBURYS S/MKTS CAMDEN", "Groceries", "debit"),
    ("ASDA SUPERSTORE MANCHESTER", "Groceries", "debit"),
    ("WAITROSE EDINBURGH FOOD", "Groceries", "debit"),
    ("LIDL UK BARKING GROCERY", "Groceries", "debit"),
    ("IGA LOCAL SUPERMARKET", "Groceries", "debit"),
    ("HARRIS FARM MARKETS FRESH", "Groceries", "debit"),
    ("BLINKIT QUICK GROCERY DELIVERY", "Groceries", "debit"),
    ("BIGBASKET ONLINE SUPERMARKET", "Groceries", "debit"),
    ("DMART READY STORE RETAIL", "Groceries", "debit"),
    ("ZEPTO 10 MINUTE GROCERY ORDER", "Groceries", "debit"),
    ("MARKS AND SPENCER SIMPLY FOOD", "Groceries", "debit"),

    # 7. Dining & Restaurants (debit)
    ("STARBUCKS COFFEE PADDINGTON", "Dining & Restaurants", "debit"),
    ("COSTA COFFEE HIGH STREET", "Dining & Restaurants", "debit"),
    ("PRET A MANGER VICTORIA STATION", "Dining & Restaurants", "debit"),
    ("GREGGS BAKERY LUNCH", "Dining & Restaurants", "debit"),
    ("MCDONALDS RESTAURANT GEORGE ST", "Dining & Restaurants", "debit"),
    ("HUNGRY JACKS FAST FOOD", "Dining & Restaurants", "debit"),
    ("UBER EATS ONLINE FOOD ORDER", "Dining & Restaurants", "debit"),
    ("DELIVEROO MEAL DELIVERY", "Dining & Restaurants", "debit"),
    ("SWIGGY RESTAURANT FOOD ORDER", "Dining & Restaurants", "debit"),
    ("ZOMATO ONLINE FOOD DELIVERY", "Dining & Restaurants", "debit"),
    ("DOMINOS PIZZA TAKEAWAY", "Dining & Restaurants", "debit"),
    ("KFC STORE FRIED CHICKEN", "Dining & Restaurants", "debit"),
    ("CAFE COFFEE DAY AIRPORT", "Dining & Restaurants", "debit"),
    ("SUBWAY SANDWICHES LUNCH", "Dining & Restaurants", "debit"),
    ("BURGER KING AIRPORT DINING", "Dining & Restaurants", "debit"),

    # 8. Transport & Travel (debit)
    ("TRANSPORT FOR LONDON TFL TRAVEL CONTACTLESS", "Transport & Travel", "debit"),
    ("TFL.GOV.UK UNDERGROUND FARE", "Transport & Travel", "debit"),
    ("NATIONAL RAIL TICKET OFFICE PADDINGTON", "Transport & Travel", "debit"),
    ("LINKT TOLL PAYMENT SYDNEY MOTORWAYS", "Transport & Travel", "debit"),
    ("TRANSURBAN TOLLWAY CHARGE", "Transport & Travel", "debit"),
    ("AMPOL SERVICE STATION FUEL", "Transport & Travel", "debit"),
    ("BP CONNECT SERVICE STATION PETROL", "Transport & Travel", "debit"),
    ("UBER *TRIP RIDESHARE SYDNEY", "Transport & Travel", "debit"),
    ("UBER TRIP PENDING RIDE LONDON", "Transport & Travel", "debit"),
    ("SHELL COLES EXPRESS PETROL", "Transport & Travel", "debit"),
    ("OLA CABS RIDESHARE TRIP", "Transport & Travel", "debit"),
    ("IRCTC TRAIN TICKET BOOKING", "Transport & Travel", "debit"),
    ("INDIGO AIRLINES FLIGHT TICKET", "Transport & Travel", "debit"),
    ("QANTAS AIRWAYS DOMESTIC AIRFARE", "Transport & Travel", "debit"),
    ("BRITISH AIRWAYS HEATHROW TRAVEL", "Transport & Travel", "debit"),
    ("CALTEX SERVICE STATION DIESEL", "Transport & Travel", "debit"),

    # 9. Utilities & Bills (debit)
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
    ("VODAFONE POSTPAID MOBILE BILL", "Utilities & Bills", "debit"),
    ("JIO PREPAID RECHARGE PLAN", "Utilities & Bills", "debit"),
    ("AIRTEL BROADBAND FIBER BILL", "Utilities & Bills", "debit"),
    ("TATA POWER MUMBAI ELECTRICITY", "Utilities & Bills", "debit"),
    ("ADANI ELECTRICITY POWER BILL", "Utilities & Bills", "debit"),

    # 10. Rent & Housing (debit)
    ("HARBOUR RESIDENTIAL RENT PAYMENT", "Rent & Housing", "debit"),
    ("RAY WHITE REAL ESTATE RENT", "Rent & Housing", "debit"),
    ("LJ HOOKER TENANCY LEASE PAYMENT", "Rent & Housing", "debit"),
    ("BODY CORPORATE STRATA LEVY", "Rent & Housing", "debit"),
    ("STRATA SCHEME QUARTERLY LEVY", "Rent & Housing", "debit"),
    ("NOBROKER MONTHLY HOUSE RENT", "Rent & Housing", "debit"),
    ("LANDLORD MONTHLY FLAT RENT", "Rent & Housing", "debit"),
    ("APARTMENT MAINTENANCE CHARGE", "Rent & Housing", "debit"),
    ("RENT PAYMENT HARBOUR PROPERTY", "Rent & Housing", "debit"),
    ("RESIDENTIAL LEASE RENTAL PAYMENT", "Rent & Housing", "debit"),

    # 11. Shopping & Retail (debit)
    ("BUNNINGS WAREHOUSE HARDWARE", "Shopping & Retail", "debit"),
    ("KMART BROADWAY RETAIL STORE", "Shopping & Retail", "debit"),
    ("JB HI-FI ELECTRONICS STRATHFIELD", "Shopping & Retail", "debit"),
    ("TARGET AUSTRALIA DEPARTMENT", "Shopping & Retail", "debit"),
    ("AMAZON MKTPLACE RETAIL ORDER", "Shopping & Retail", "debit"),
    ("AMAZON.CO.UK DIGITAL RETAIL", "Shopping & Retail", "debit"),
    ("ASOS ONLINE FASHION CLOTHING", "Shopping & Retail", "debit"),
    ("ZARA FASHION RETAIL STORE", "Shopping & Retail", "debit"),
    ("UNIQLO CLOTHING SYDNEY", "Shopping & Retail", "debit"),
    ("APPLE STORE RETAIL PURCHASE", "Shopping & Retail", "debit"),
    ("UPI/621848103425/DR/Amazon/RATN/amazonpay/Reques", "Shopping & Retail", "debit"),
    ("UPI/621859612800/DR/Flipka/YESB/flipkart./OD3382", "Shopping & Retail", "debit"),
    ("UPI/622163379669/DR/Meesho/YESB/paytm-177/UPI In", "Shopping & Retail", "debit"),
    ("MYNTRA FASHION SHOPPING ONLINE", "Shopping & Retail", "debit"),
    ("NYKAA BEAUTY & COSMETICS", "Shopping & Retail", "debit"),
    ("IKEA FURNITURE HOMEWARE STORE", "Shopping & Retail", "debit"),

    # 12. Healthcare & Pharmacy (debit)
    ("CHEMIST WAREHOUSE PHARMACY", "Healthcare & Pharmacy", "debit"),
    ("PRICELINE PHARMACY PRESCRIPTION", "Healthcare & Pharmacy", "debit"),
    ("BOOTS UK CHEMIST OXFORD ST", "Healthcare & Pharmacy", "debit"),
    ("BUPA DENTAL CLINIC SURGERY", "Healthcare & Pharmacy", "debit"),
    ("PRIMARY HEALTHCARE GP CLINIC", "Healthcare & Pharmacy", "debit"),
    ("VISION AUSTRALIA OPTOMETRIST", "Healthcare & Pharmacy", "debit"),
    ("PHARMEASY ONLINE MEDICINE", "Healthcare & Pharmacy", "debit"),
    ("1MG HEALTHCARE PHARMACY", "Healthcare & Pharmacy", "debit"),
    ("APOLLO PHARMACY MEDICAL STORE", "Healthcare & Pharmacy", "debit"),
    ("NETMEDS DRUGS ONLINE ORDER", "Healthcare & Pharmacy", "debit"),
    ("DENTAL CARE ORAL SURGERY", "Healthcare & Pharmacy", "debit"),
    ("OPTICAL DISPENSARY EYEGLASSES", "Healthcare & Pharmacy", "debit"),

    # 13. Insurance (debit)
    ("ALLIANZ CAR INSURANCE MONTHLY", "Insurance", "debit"),
    ("NRMA COMPREHENSIVE VEHICLE POLICY", "Insurance", "debit"),
    ("MEDIBANK PRIVATE HEALTH COVER", "Insurance", "debit"),
    ("AVIVA HOME & CONTENTS INSURANCE", "Insurance", "debit"),
    ("BUPA HEALTHCARE INSURANCE D/D", "Insurance", "debit"),
    ("ADMIRAL CAR INSURANCE POLICY", "Insurance", "debit"),
    ("HDFC ERGO HEALTH INSURANCE", "Insurance", "debit"),
    ("ICICI LOMBARD MOTOR INSURANCE", "Insurance", "debit"),
    ("STAR HEALTH ALLIED INSURANCE", "Insurance", "debit"),
    ("AIA LIFE INSURANCE PREMIUM", "Insurance", "debit"),

    # 14. Fees & Charges (debit)
    ("MONTHLY ACCOUNT SERVICE FEE", "Fees & Charges", "debit"),
    ("OVERDRAWN ACCOUNT ADMINISTRATION CHARGE", "Fees & Charges", "debit"),
    ("INTERNATIONAL TRANSACTION CONVERSION FEE", "Fees & Charges", "debit"),
    ("OVERDRAFT USAGE FEE", "Fees & Charges", "debit"),
    ("NON-NETWORK ATM OPERATOR SURCHARGE", "Fees & Charges", "debit"),
    ("LATE PAYMENT FINANCE CHARGE", "Fees & Charges", "debit"),
    ("CARD REPLACEMENT ISSUANCE FEE", "Fees & Charges", "debit"),
    ("ANNUAL CREDIT CARD RECURRING FEE", "Fees & Charges", "debit"),
    ("FOREIGN CURRENCY EXCHANGE ADMIN CHARGE", "Fees & Charges", "debit"),

    # 15. Loan & Credit Payments (debit)
    ("CBA HOME LOAN REPAYMENT", "Loan & Credit Payments", "debit"),
    ("ANZ MORTGAGE DIRECT DEBIT", "Loan & Credit Payments", "debit"),
    ("WESTPAC PERSONAL LOAN INSTALLMENT", "Loan & Credit Payments", "debit"),
    ("NAB CREDIT CARD AUTOPAY MINIMUM", "Loan & Credit Payments", "debit"),
    ("BARCLAYCARD MONTHLY CARD REPAYMENT", "Loan & Credit Payments", "debit"),
    ("SANTANDER CAR FINANCE LEASE", "Loan & Credit Payments", "debit"),
    ("HDFC HOME LOAN EMI AUTODEBIT", "Loan & Credit Payments", "debit"),
    ("SBI MORTGAGE LOAN REPAYMENT", "Loan & Credit Payments", "debit"),
    ("BAJAJ FINSERV EMI DEBIT", "Loan & Credit Payments", "debit"),
    ("MORTGAGE PRINCIPAL AND INTEREST PAYMENT", "Loan & Credit Payments", "debit"),

    # 16. Taxes & Government (debit)
    ("AUSTRALIAN TAXATION OFFICE ATO PAYMENT", "Taxes & Government", "debit"),
    ("ATO ACTIVITY STATEMENT DEBIT", "Taxes & Government", "debit"),
    ("HMRC SELF ASSESSMENT PAYMENT", "Taxes & Government", "debit"),
    ("HM REVENUE & CUSTOMS TAX D/D", "Taxes & Government", "debit"),
    ("CITY COUNCIL LOCAL RATES NOTICE", "Taxes & Government", "debit"),
    ("SERVICE NSW DRIVER LICENCE RENEWAL", "Taxes & Government", "debit"),
    ("STATE REVENUE OFFICE STAMP DUTY", "Taxes & Government", "debit"),
    ("INCOME TAX DEPARTMENT E-FILING", "Taxes & Government", "debit"),
    ("GST TAX PAYMENT CHALLAN", "Taxes & Government", "debit"),
    ("DVLA VEHICLE ROAD TAX", "Taxes & Government", "debit"),

    # 17. Education & Childcare (debit)
    ("UNIVERSITY OF SYDNEY TUITION FEES", "Education & Childcare", "debit"),
    ("UNSW SEMESTER FEE PAYMENT", "Education & Childcare", "debit"),
    ("LITTLE ANGELS EARLY LEARNING DAYCARE", "Education & Childcare", "debit"),
    ("GOODSTART EARLY LEARNING CHILDCARE", "Education & Childcare", "debit"),
    ("GRAMMAR SCHOOL TERM EDUCATION", "Education & Childcare", "debit"),
    ("TAFE VOCATIONAL COURSE ENROLMENT", "Education & Childcare", "debit"),
    ("UDEMY ONLINE LEARNING COURSE", "Education & Childcare", "debit"),
    ("COURSERA SUBSCRIPTION EDUCATION", "Education & Childcare", "debit"),
    ("BYJUS LEARNING TUITION FEES", "Education & Childcare", "debit"),
    ("OXFORD UNIVERSITY COLLEGE TUITION", "Education & Childcare", "debit"),

    # 18. Donations & Charity (debit)
    ("AUSTRALIAN RED CROSS DONATION", "Donations & Charity", "debit"),
    ("SALVATION ARMY CHARITABLE GIFT", "Donations & Charity", "debit"),
    ("UNICEF AUSTRALIA MONTHLY GIVING", "Donations & Charity", "debit"),
    ("CANCER COUNCIL FUNDRAISING", "Donations & Charity", "debit"),
    ("RSPCA ANIMAL SHELTER DONATION", "Donations & Charity", "debit"),
    ("OXFAM DIRECT DEBIT CHARITY", "Donations & Charity", "debit"),
    ("PM CARES RELIEF FUND", "Donations & Charity", "debit"),
    ("CRY CHILD RIGHTS AND YOU", "Donations & Charity", "debit"),
    ("AMNESTY INTERNATIONAL MONTHLY GIFT", "Donations & Charity", "debit"),

    # 19. Personal Care (debit)
    ("JUST CUTS HAIRDRESSER SALON", "Personal Care", "debit"),
    ("BARBER SHOP HAIRCUT & SHAVE", "Personal Care", "debit"),
    ("ENDOTA DAY SPA MASSAGE TREATMENT", "Personal Care", "debit"),
    ("TONI & GUY HAIR SALON", "Personal Care", "debit"),
    ("SEPHORA COSMETICS & SKINCARE", "Personal Care", "debit"),
    ("URBAN COMPANY SALON AT HOME", "Personal Care", "debit"),
    ("ENRICH BEAUTY SALON SERVICES", "Personal Care", "debit"),
    ("BEAUTY CLINIC FACIAL SKINCARE", "Personal Care", "debit"),
    ("NAIL SALON MANICURE PEDICURE", "Personal Care", "debit"),

    # 20. Investments & Wealth (both)
    ("VANGUARD DIVERSIFIED GROWTH ETF", "Investments & Wealth", "debit"),
    ("COMMSEC SHARE TRADING SETTLEMENT", "Investments & Wealth", "debit"),
    ("STAKE US EQUITIES BROKERAGE", "Investments & Wealth", "debit"),
    ("AUSTRALIAN SUPERANNUATION CONTRIBUTION", "Investments & Wealth", "credit"),
    ("BETASHARES AUSTRALIA INVESTMENT", "Investments & Wealth", "debit"),
    ("HARGREAVES LANSDOWN ISA FUND", "Investments & Wealth", "debit"),
    ("NACH DR INW - TP ACH NIPPON IND MF", "Investments & Wealth", "debit"),
    ("HDFC MUTUAL FUND SIP AUTODEBIT", "Investments & Wealth", "debit"),
    ("SBI MUTUAL FUND DIRECT INVESTMENT", "Investments & Wealth", "debit"),
    ("ZERODHA BROKING EQUITY FUNDS", "Investments & Wealth", "debit"),
    ("GROWW MUTUAL FUND SIP", "Investments & Wealth", "debit"),

    # 21. Entertainment & Subscriptions (debit)
    ("NETFLIX STREAMING MONTHLY", "Entertainment & Subscriptions", "debit"),
    ("SPOTIFY PREMIUM AUDIO", "Entertainment & Subscriptions", "debit"),
    ("DISNEY PLUS STREAMING SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),
    ("YOUTUBE PREMIUM MONTHLY", "Entertainment & Subscriptions", "debit"),
    ("APPLE SERVICES ITUNES STORE", "Entertainment & Subscriptions", "debit"),
    ("STEAM GAMES VALVE CORPORATION", "Entertainment & Subscriptions", "debit"),
    ("PLAYSTATION NETWORK SONY", "Entertainment & Subscriptions", "debit"),
    ("ANYTIME FITNESS 24/7 GYM", "Entertainment & Subscriptions", "debit"),
    ("FITNESS FIRST GYM MEMBERSHIP", "Entertainment & Subscriptions", "debit"),
    ("AMAZON PRIME SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),
    ("HOTSTAR SPECIALS VIP STREAMING", "Entertainment & Subscriptions", "debit"),
    ("XBOX GAME PASS SUBSCRIPTION", "Entertainment & Subscriptions", "debit"),

    # 22. Cash Withdrawal (debit)
    ("ATM WITHDRAWAL LOCAL BRANCH", "Cash Withdrawal", "debit"),
    ("CBA ATM CASH DISPENSE", "Cash Withdrawal", "debit"),
    ("WESTPAC CASH OUT STORE", "Cash Withdrawal", "debit"),
    ("BARCLAYS BANK ATM CASH WDL", "Cash Withdrawal", "debit"),
    ("CASH WITHDRAWAL HIGH STREET ATM", "Cash Withdrawal", "debit"),
    ("STATE BANK ATM CASH WITHDRAWAL", "Cash Withdrawal", "debit"),
    ("HDFC BANK ATM MONEY OUT", "Cash Withdrawal", "debit"),
    ("AUTOMATED TELLER MACHINE CASH DEBIT", "Cash Withdrawal", "debit"),

    # 23. Transfers Out (debit)
    ("TRANSFER TO SAVINGS ACCOUNT", "Transfers Out", "debit"),
    ("NETBANK INTERNAL FUNDS TRANSFER", "Transfers Out", "debit"),
    ("OSKO PAYMENT SENT TO CONTRACTOR", "Transfers Out", "debit"),
    ("UPI/192425475385/DR/BHIM/ICIC/bhimrecha/NO REM", "Transfers Out", "debit"),
    ("UPI/211437195836/DR/BHIM/ICIC/bhimrecha/NO REM", "Transfers Out", "debit"),
    ("UPI/142006840106/DR/BALVI/UTIB/704625713/NO REM", "Transfers Out", "debit"),
    ("IMPS OUTWARD FUNDS TRANSFER", "Transfers Out", "debit"),
    ("NEFT DR FUNDS TRANSFER TO VENDOR", "Transfers Out", "debit"),
    ("FASTER PAYMENTS OUTGOING TO PEER", "Transfers Out", "debit"),
    ("DIRECT DEBIT TRANSFER TO EXTERNAL", "Transfers Out", "debit"),

    # 24. Other / Unclassified (both)
    ("MISCELLANEOUS EXPENSE UNKNOWN", "Other / Unclassified", "debit"),
    ("SUNDRY DEBIT UNRECONCILED", "Other / Unclassified", "debit"),
    ("GENERAL LEDGER ADJUSTMENT ENTRY", "Other / Unclassified", "both"),
    ("UNIDENTIFIED LINE TRANSACTION ITEM", "Other / Unclassified", "both"),
]


# Isolated held-out test evaluation set: UNSEEN merchants and narrations not in training samples!
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
