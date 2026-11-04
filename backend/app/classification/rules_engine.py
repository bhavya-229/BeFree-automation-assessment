"""Deterministic rule engine with keyword inverted index, negative matching, and specificity scoring."""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ClassificationRule(BaseModel):
    """Deterministic classification rule definition with negative guardrails."""

    rule_id: str
    category: str
    subcategory: Optional[str] = None
    keywords: List[str]
    exclude_keywords: List[str] = Field(default_factory=list)
    direction: str = "both"  # "debit", "credit", or "both"
    priority: int = 10       # Higher number = higher precedence
    confidence: float = 0.95


# Seed list of deterministic keyword rules covering AU, UK, and universal patterns
DEFAULT_RULES: List[ClassificationRule] = [
    # --- Income ---
    # Salary & Wages
    ClassificationRule(
        rule_id="RULE_SALARY_01",
        category="Salary & Wages",
        subcategory="Regular Pay",
        keywords=["SALARY", "PAYROLL", "WAGES", "DIRECT CREDIT PAY", "EMPLOYER PAY", "REMPAY", "SERVICES PAYROLL"],
        exclude_keywords=["REFUND", "REVERSAL", "REBATE", "DIVIDEND"],
        direction="credit",
        priority=20,
        confidence=0.98,
    ),
    # Transfers In (Incoming Funds & P2P)
    ClassificationRule(
        rule_id="RULE_TRANS_IN_01",
        category="Transfers In",
        subcategory="P2P Transfer",
        keywords=["PAYID TRANSFER RECEIVED", "PAYID RECEIVED", "PAYID", "OSKO RECEIVED", "TRANSFER FROM", "DIRECT CREDIT PAYID"],
        exclude_keywords=["REFUND", "REBATE", "DIVIDEND", "INTEREST"],
        direction="credit",
        priority=18,
        confidence=0.95,
    ),
    # Refunds & Cashbacks
    ClassificationRule(
        rule_id="RULE_REFUND_01",
        category="Refunds & Cashbacks",
        subcategory="Merchant Refund",
        keywords=["REFUND - RETAIL PURCHASE", "RETAIL PURCHASE REFUND", "REFUND", "MERCHANT REFUND", "CASHBACK", "PURCHASE REVERSAL", "REVERSAL"],
        exclude_keywords=["FEE REVERSAL", "INTEREST REVERSAL"],
        direction="credit",
        priority=18,
        confidence=0.96,
    ),
    # Healthcare & Government Rebates
    ClassificationRule(
        rule_id="RULE_HEALTH_AU_02",
        category="Healthcare & Pharmacy",
        subcategory="Rebate",
        keywords=["MEDICARE REBATE", "MEDICARE", "CENTRELINK REBATE", "CENTRELINK", "PRIVATE HEALTH REBATE"],
        exclude_keywords=["PHARMACY PURCHASE", "DOCTOR PAYMENT"],
        direction="credit",
        priority=18,
        confidence=0.98,
    ),
    # Interest Earned
    ClassificationRule(
        rule_id="RULE_INT_01",
        category="Interest & Investments",
        subcategory="Bank Interest",
        keywords=["INTEREST PAID", "CREDIT INTEREST", "INTEREST EARNED", "SAVINGS INTEREST"],
        direction="credit",
        priority=18,
        confidence=0.98,
    ),

    # --- Core Living & Housing Expenses ---
    # Rent & Housing
    ClassificationRule(
        rule_id="RULE_RENT_AU_01",
        category="Rent & Housing",
        subcategory="Rent",
        keywords=["RENT PAYMENT", "RESIDENTIAL RENT", "HARBOUR PROPERTY", "REAL ESTATE RENT", "BODY CORPORATE", "STRATA LEVY", "LANDLORD", "RENT"],
        exclude_keywords=["CURRENT ACCOUNT", "PARENT", "DIFFERENT", "APPRENTICE", "RENTAL CAR", "MORTGAGE", "CAR RENTAL"],
        direction="debit",
        priority=18,
        confidence=0.88,
    ),
    # Loan & Credit Repayments (Mortgages, Loans, Credit Cards)
    ClassificationRule(
        rule_id="RULE_LOAN_01",
        category="Loan & Credit Payments",
        subcategory="Mortgage",
        keywords=["MORTGAGE REPAYMENT", "MORTGAGE PAYMENT", "MORTGAGE", "HOME LOAN", "PERSONAL LOAN", "CAR LOAN", "CREDIT CARD REPAYMENT", "CREDIT CARD AUTOPAY"],
        exclude_keywords=["INTEREST PAID", "SAVINGS INTEREST"],
        direction="debit",
        priority=20,
        confidence=0.96,
    ),

    # --- Groceries ---
    ClassificationRule(
        rule_id="RULE_GROC_AU_01",
        category="Groceries",
        subcategory="Supermarket",
        keywords=["WOOLWORTHS", "COLES", "ALDI", "IGA SUPERMARKET", "HARRIS FARM", "TRADER JOES", "WHOLE FOODS", "SAFEWAY", "KROGER"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_GROC_UK_01",
        category="Groceries",
        subcategory="Supermarket",
        keywords=["TESCO", "SAINSBURYS", "ASDA", "MORRISONS", "WAITROSE", "CO-OP FOOD", "LIDL"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),

    # --- Utilities & Bills ---
    ClassificationRule(
        rule_id="RULE_UTIL_AU_01",
        category="Utilities & Bills",
        subcategory="Internet & Mobile",
        keywords=["TELSTRA MOBILE BILL", "TELSTRA", "OPTUS", "VODAFONE", "TPG INTERNET", "AUSSIE BROADBAND", "BELONG"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_AU_02",
        category="Utilities & Bills",
        subcategory="Electricity & Gas",
        keywords=["AGL ENERGY", "ORIGIN ENERGY", "ENERGYAUSTRALIA", "SYDNEY WATER", "YARRA VALLEY WATER"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_UK_01",
        category="Utilities & Bills",
        subcategory="Electricity & Gas",
        keywords=["BRITISH GAS", "EDF ENERGY", "E.ON", "OCTOPUS ENERGY", "THAMES WATER", "SEVERN TRENT"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_UK_02",
        category="Utilities & Bills",
        subcategory="Internet & Mobile",
        keywords=["EE MOBILE", "O2 UK", "THREE UK", "BT BILL", "SKY DIGITAL", "VIRGIN MEDIA"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),

    # --- Transport & Travel ---
    # Road Tolls (AU)
    ClassificationRule(
        rule_id="RULE_TRANS_AU_01",
        category="Transport & Travel",
        subcategory="Tolls",
        keywords=["LINKT", "TRANSURBAN", "EASTLINK", "ROADS AND MARITIME", "TOLL PAYMENT", "TOLL"],
        exclude_keywords=["TOLLWAY RESTAURANT", "HOTEL"],
        direction="debit",
        priority=15,
        confidence=0.92,
    ),
    # Fuel Brands & Service Stations
    ClassificationRule(
        rule_id="RULE_TRANS_AU_02",
        category="Transport & Travel",
        subcategory="Fuel",
        keywords=["AMPOL", "CALTEX", "BP CONNECT", "7-ELEVEN FUEL", "UNITED PETROLEUM", "EXXON", "CHEVRON", "MOBIL", "TEXACO"],
        exclude_keywords=["MOBILE", "OPTUS", "TELSTRA", "VODAFONE", "EE MOBILE"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_TRANS_AU_04",
        category="Transport & Travel",
        subcategory="Fuel",
        keywords=["CARD PURCHASE - FUEL STATION", "FUEL STATION", "SERVICE STATION", "PETROL", "SERVO", "HIGHWAY GAS STOP", "TRUCK STOP"],
        direction="debit",
        priority=15,
        confidence=0.90,
    ),
    # Transit Smartcards & Rail
    ClassificationRule(
        rule_id="RULE_TRANS_AU_03",
        category="Transport & Travel",
        subcategory="Public Transport",
        keywords=["OPAL TOP UP", "OPAL", "MYKI", "METROCARD", "TRANSLINK", "TRANSPORT FOR NSW", "SUBWAY METRO", "SUBWAY TICKET", "SUBWAY STATION"],
        exclude_keywords=["OPALINE", "SUBWAY RESTAURANT", "SUBWAY SANDWICH", "SUBWAY STORE"],
        direction="debit",
        priority=16,
        confidence=0.96,
    ),
    ClassificationRule(
        rule_id="RULE_TRANS_UK_01",
        category="Transport & Travel",
        subcategory="Public Transport",
        keywords=["TRANSPORT FOR LONDON", "TFL", "NATIONAL RAIL", "LNER", "GREAT WESTERN"],
        direction="debit",
        priority=18,
        confidence=0.98,
    ),
    # Rideshare & Taxi
    ClassificationRule(
        rule_id="RULE_TRANS_UNI_01",
        category="Transport & Travel",
        subcategory="Rideshare & Taxi",
        keywords=["UBER TRIP", "UBER *TRIP", "DIDI", "OLA", "CABCHARGE", "LYFT"],
        exclude_keywords=["COLA", "GOLA", "GRANOLA", "UBER EATS"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    # Airlines & Hotels
    ClassificationRule(
        rule_id="RULE_TRAVEL_01",
        category="Transport & Travel",
        subcategory="Airlines",
        keywords=["AIRBNB", "DELTA AIRLINES", "AMERICAN AIRLINES", "EMIRATES", "QANTAS", "VIRGIN AUSTRALIA", "HERTZ", "ENTERPRISE RENT-A-CAR", "HILTON"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),

    # --- Dining & Restaurants ---
    ClassificationRule(
        rule_id="RULE_DINE_01",
        category="Dining & Restaurants",
        subcategory="Cafes & Coffee",
        keywords=["STARBUCKS", "COSTA COFFEE", "PRET A MANGER", "GREGGS", "NERO", "BOOST JUICE"],
        exclude_keywords=["NERO SOFTWARE"],
        direction="debit",
        priority=14,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_DINE_02",
        category="Dining & Restaurants",
        subcategory="Takeaway & Delivery",
        keywords=["MCDONALDS", "HUNGRY JACKS", "KFC", "SUBWAY RESTAURANT", "SUBWAY SANDWICH", "SUBWAY STORE", "UBER EATS", "DELIVEROO", "DOORDASH", "JUST EAT", "TACO BELL", "CHIPOTLE"],
        direction="debit",
        priority=15,
        confidence=0.96,
    ),
    # Generic Cafes & Dining (Tier 3: Lower confidence 0.70 to allow ML corroboration)
    ClassificationRule(
        rule_id="RULE_DINE_03",
        category="Dining & Restaurants",
        subcategory="Cafes & Coffee",
        keywords=["CARD PURCHASE - CAFE", "CAFE", "COFFEE", "BAKERY", "ESPRESSO", "ROASTER", "BISTRO", "DINER", "PANERA BREAD", "APPLEBEES", "BURGER KING"],
        direction="debit",
        priority=10,
        confidence=0.70,
    ),

    # --- Shopping & Retail ---
    ClassificationRule(
        rule_id="RULE_SHOP_AU_01",
        category="Shopping & Retail",
        subcategory="Home & Hardware",
        keywords=["BUNNINGS", "KMART", "TARGET STORE", "TARGET RETAIL", "TARGET AUSTRALIA", "BIG W", "JB HI-FI", "OFFICEWORKS", "MYER"],
        exclude_keywords=["TARGET SAVINGS", "TARGET SUPER", "TARGET FUND"],
        direction="debit",
        priority=14,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_SHOP_UK_01",
        category="Shopping & Retail",
        subcategory="Clothing",
        keywords=["MARKS AND SPENCER", "PRIMARK", "NEXT RETAIL", "NEXT DIRECT", "NEXT DIRECTORY", "NEXT CLOTHING", "JOHN LEWIS", "ARGOS", "CURRYS"],
        direction="debit",
        priority=14,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_SHOP_UNI_01",
        category="Shopping & Retail",
        subcategory="Online Shopping",
        keywords=["AMAZON MARKETPLACE", "EBAY", "APPLE STORE", "GOOGLE STORE"],
        exclude_keywords=["AMAZON PRIME", "AMZN PRIME", "APPLE.COM/BILL", "ITUNES.COM"],
        direction="debit",
        priority=12,
        confidence=0.92,
    ),
    ClassificationRule(
        rule_id="RULE_SHOP_UNI_02",
        category="Shopping & Retail",
        subcategory="Online Shopping",
        keywords=["WALMART", "COSTCO", "HOME DEPOT", "IKEA", "ETSY", "ALIEXPRESS", "NIKE", "SEPHORA", "WAYFAIR", "ZARA", "BARNES & NOBLE"],
        direction="debit",
        priority=12,
        confidence=0.92,
    ),

    # --- Healthcare & Pharmacy ---
    ClassificationRule(
        rule_id="RULE_HEALTH_01",
        category="Healthcare & Pharmacy",
        subcategory="Pharmacy",
        keywords=["CHEMIST WAREHOUSE", "PRICELINE", "BOOTS PHARMACY", "SUPERDRUG", "PHARMACY", "MEDICAL CENTRE", "CVS PHARMACY", "WALGREENS", "RITE AID", "LOCAL HOSPITAL", "URGENT CARE"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),

    # --- Insurance ---
    ClassificationRule(
        rule_id="RULE_INSUR_01",
        category="Insurance",
        subcategory="General Insurance",
        keywords=["INSURANCE PREMIUM", "INSURANCE", "BUPA", "MEDIBANK", "ALLIANZ", "NRMA", "AAMI", "QBE", "RACV", "AVIVA", "AXA"],
        direction="debit",
        priority=18,
        confidence=0.96,
    ),

    # --- Entertainment & Subscriptions ---
    ClassificationRule(
        rule_id="RULE_ENT_01",
        category="Entertainment & Subscriptions",
        subcategory="Streaming Services",
        keywords=["NETFLIX", "SPOTIFY", "DISNEY PLUS", "DISNEY+", "YOUTUBE PREMIUM", "APPLE MUSIC", "AUDIBLE", "APPLE DIGITAL SUBSCRIPTION", "AMAZON PRIME SUBSCRIPTION", "PRIME VIDEO", "STEAM GAMES", "STEAM", "HULU", "HBO MAX", "NINTENDO", "PLAYSTATION", "XBOX LIVE"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),

    # --- Taxes & Government ---
    ClassificationRule(
        rule_id="RULE_TAX_01",
        category="Taxes & Government",
        subcategory="Income Tax",
        keywords=["ATO TAX PAYMENT", "ATO PAYMENT", "AUSTRALIAN TAXATION OFFICE", "HMRC TAX", "COUNCIL RATES", "COUNCIL TAX", "STAMP DUTY", "TRAFFIC FINE", "INFRINGEMENTS"],
        direction="debit",
        priority=18,
        confidence=0.98,
    ),

    # --- Education & Childcare ---
    ClassificationRule(
        rule_id="RULE_EDU_01",
        category="Education & Childcare",
        subcategory="University",
        keywords=["UNIVERSITY TUITION", "UNIVERSITY", "SCHOOL FEES", "TAFE", "DAYCARE", "COLLEGE TUITION", "COURSERA", "UDEMY"],
        direction="debit",
        priority=16,
        confidence=0.95,
    ),

    # --- Donations & Charity ---
    ClassificationRule(
        rule_id="RULE_DONATE_01",
        category="Donations & Charity",
        subcategory="Charity",
        keywords=["RED CROSS", "SALVATION ARMY", "UNICEF", "CANCER COUNCIL", "CHARITY DONATION", "DONATION"],
        direction="debit",
        priority=16,
        confidence=0.95,
    ),

    # --- Personal Care ---
    ClassificationRule(
        rule_id="RULE_CARE_01",
        category="Personal Care",
        subcategory="Hair & Beauty",
        keywords=["HAIRDRESSER", "BARBER", "BEAUTY SALON", "MASSAGE", "DAY SPA"],
        direction="debit",
        priority=12,
        confidence=0.75,
    ),

    # --- Investments & Wealth ---
    ClassificationRule(
        rule_id="RULE_INVEST_01",
        category="Investments & Wealth",
        subcategory="Shares & Brokerage",
        keywords=["VANGUARD", "COMMSEC", "STAKE", "SUPERANNUATION", "CRYPTO EXCHANGE", "COINBASE", "BINANCE", "MANAGED FUND"],
        direction="both",
        priority=16,
        confidence=0.95,
    ),

    # --- Bank Fees & Charges ---
    ClassificationRule(
        rule_id="RULE_FEES_01",
        category="Fees & Charges",
        subcategory="Bank Fees",
        keywords=["ACCOUNT FEE", "MONTHLY FEE", "OVERDRAWN FEE", "OVERDRAFT INTEREST", "INTERNATIONAL TRANSACTION FEE", "LATE PAYMENT FEE"],
        direction="debit",
        priority=18,
        confidence=0.98,
    ),

    # --- Cash Withdrawal & Transfers Out ---
    ClassificationRule(
        rule_id="RULE_CASH_01",
        category="Cash Withdrawal",
        subcategory="ATM Withdrawal",
        keywords=["ATM WITHDRAWAL", "ATM WDL", "CASH WITHDRAWAL", "BRANCH CASH WDL"],
        direction="debit",
        priority=20,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_TRANS_OUT_01",
        category="Transfers Out",
        subcategory="Self Transfer",
        keywords=["TRANSFER TO SAVINGS", "NETBANK TRANSFER", "OSKO PAYMENT", "INTERNAL TRANSFER", "TRANSFER TO"],
        exclude_keywords=["LANDLORD", "RENT", "MORTGAGE", "COUNCIL", "TAX", "ATO", "HMRC", "DONATION", "TUITION"],
        direction="debit",
        priority=14,
        confidence=0.90,
    ),

    # ─── India-specific rules ──────────────────────────────────────────────────

    # UPI P2P credits (money received via UPI)
    ClassificationRule(
        rule_id="RULE_UPI_IN_01",
        category="Transfers In",
        subcategory="UPI Transfer",
        keywords=["UPI/CR", "UPI//CR", "IMPS/CR", "NEFT/CR", "BHIM UPI", "OSKO RECEIVED"],
        exclude_keywords=["AMAZON", "FLIPKART", "SWIGGY", "ZOMATO", "PAYTM MERCHANT", "MEESHO", "MYNTRA", "PHARMEASY"],
        direction="credit",
        priority=15,
        confidence=0.88,
    ),
    # UPI P2P debits (money sent via UPI — generic/unclassified merchant)
    ClassificationRule(
        rule_id="RULE_UPI_OUT_01",
        category="Transfers Out",
        subcategory="UPI Transfer",
        keywords=["UPI/DR", "UPI//DR", "IMPS/DR", "NEFT/DR"],
        exclude_keywords=["AMAZON", "FLIPKART", "SWIGGY", "ZOMATO", "MEESHO", "MYNTRA", "PHARMEASY",
                          "NACH", "BLINKIT", "BIGBASKET", "SMARTBUY", "ONEMONEY", "PHONEPAY"],
        direction="debit",
        priority=13,
        confidence=0.75,
    ),
    # Amazon Pay (UPI debit to Amazon)
    ClassificationRule(
        rule_id="RULE_UPI_AMAZON_01",
        category="Shopping & Retail",
        subcategory="Online Marketplace",
        keywords=["AMAZON", "AMAZONPAY", "AMAZON PAY"],
        exclude_keywords=["PRIME", "AMAZON PRIME", "PRIME VIDEO", "PRIME SUBSCRIPTION"],
        direction="debit",
        priority=17,
        confidence=0.95,
    ),
    # Flipkart (UPI debit to Flipkart)
    ClassificationRule(
        rule_id="RULE_UPI_FLIPKART_01",
        category="Shopping & Retail",
        subcategory="Online Marketplace",
        keywords=["FLIPKART", "FLIPKA", "FLIPK"],
        direction="debit",
        priority=17,
        confidence=0.95,
    ),
    # Meesho (online shopping)
    ClassificationRule(
        rule_id="RULE_UPI_MEESHO_01",
        category="Shopping & Retail",
        subcategory="Online Marketplace",
        keywords=["MEESHO"],
        direction="debit",
        priority=17,
        confidence=0.93,
    ),
    # Myntra (fashion)
    ClassificationRule(
        rule_id="RULE_UPI_MYNTRA_01",
        category="Shopping & Retail",
        subcategory="Fashion",
        keywords=["MYNTRA"],
        direction="debit",
        priority=17,
        confidence=0.93,
    ),
    # Swiggy / Zomato (food delivery)
    ClassificationRule(
        rule_id="RULE_UPI_FOOD_01",
        category="Dining & Restaurants",
        subcategory="Food Delivery",
        keywords=["SWIGGY", "ZOMATO"],
        direction="debit",
        priority=17,
        confidence=0.95,
    ),
    # Blinkit / BigBasket (grocery delivery)
    ClassificationRule(
        rule_id="RULE_UPI_GROC_IN_01",
        category="Groceries",
        subcategory="Online Grocery",
        keywords=["BLINKIT", "BIGBASKET", "GROFER"],
        direction="debit",
        priority=17,
        confidence=0.95,
    ),
    # PharmEasy / 1mg / Netmeds (pharmacy)
    ClassificationRule(
        rule_id="RULE_UPI_PHARMA_IN_01",
        category="Healthcare & Pharmacy",
        subcategory="Online Pharmacy",
        keywords=["PHARMEASY", "PHARME", "1MG", "NETMEDS", "APOLLO PHARMACY", "MEDPLUS"],
        direction="debit",
        priority=17,
        confidence=0.93,
    ),
    # NACH / SIP / Mutual Funds auto-debit
    ClassificationRule(
        rule_id="RULE_NACH_MF_01",
        category="Investments & Wealth",
        subcategory="Mutual Funds",
        keywords=["NACH DR INW", "NIPPON IND MF", "NIPPON MF", "HDFC MF", "SBI MF",
                  "ICICI PRU MF", "AXIS MF", "KOTAK MF", "MIRAE MF", "DSP MF",
                  "PARAG PARIKH", "NAVI MF", "MOTILAL MF"],
        direction="debit",
        priority=18,
        confidence=0.96,
    ),
    # NACH generic auto-debit (insurance, loan EMI etc.)
    ClassificationRule(
        rule_id="RULE_NACH_01",
        category="Loan & Credit Payments",
        subcategory="EMI Auto-debit",
        keywords=["NACH DR", "NACH DEBIT", "ECS DR", "ECS DEBIT"],
        exclude_keywords=["NIPPON MF", "HDFC MF", "SBI MF", "ICICI PRU MF", "AXIS MF",
                          "KOTAK MF", "MIRAE MF", "INW"],
        direction="debit",
        priority=16,
        confidence=0.88,
    ),
    # SmartBuy / Jio / Paytm merchant debits
    ClassificationRule(
        rule_id="RULE_UPI_RECHARGE_IN_01",
        category="Utilities & Bills",
        subcategory="Mobile Recharge",
        keywords=["SMARTBUY", "JIOPAY", "JIO RECHARGE", "PAYTM RECHARGE", "PHONEPE RECHARGE",
                  "ONEMONEY", "PHONEPAY"],
        direction="debit",
        priority=17,
        confidence=0.90,
    ),
    # Flipkart refund (credit from Flipkart)
    ClassificationRule(
        rule_id="RULE_UPI_FLIPKART_REFUND_01",
        category="Refunds & Cashbacks",
        subcategory="Merchant Refund",
        keywords=["FLIPKART", "FLIPKA"],
        direction="credit",
        priority=17,
        confidence=0.93,
    ),
]


class RuleEngine:
    """Fast deterministic rule engine using negative guardrails and specificity scoring."""

    def __init__(self, rules: Optional[List[ClassificationRule]] = None):
        self.rules = sorted(rules or DEFAULT_RULES, key=lambda r: r.priority, reverse=True)

    def classify(
        self, description: str, direction: str = "debit"
    ) -> Optional[Tuple[str, Optional[str], float, str, List[str]]]:
        """Match description against rules with negative guardrails and specificity-weighted ranking."""
        upper_desc = description.upper()

        candidates: List[Tuple[float, ClassificationRule, List[str]]] = []

        for rule in self.rules:
            # Check direction constraint if specified
            if rule.direction != "both" and direction != "both":
                if rule.direction != direction:
                    continue

            # Check negative exclusion keywords first
            excluded = False
            for ex_kw in rule.exclude_keywords:
                escaped_ex = re.escape(ex_kw)
                if re.search(rf"(?<!\w){escaped_ex}(?!\w)", upper_desc):
                    excluded = True
                    break
            if excluded:
                continue

            matched_keywords: List[str] = []
            max_kw_len = 0
            max_kw_words = 0

            for kw in rule.keywords:
                escaped = re.escape(kw)
                pattern = rf"(?<!\w){escaped}(?!\w)"
                if re.search(pattern, upper_desc):
                    matched_keywords.append(kw)
                    w_count = len(kw.split())
                    if w_count > max_kw_words or (w_count == max_kw_words and len(kw) > max_kw_len):
                        max_kw_words = w_count
                        max_kw_len = len(kw)

            if matched_keywords:
                # Specificity score = (priority * 100) + (word_count * 20) + char_length
                spec_score = (rule.priority * 100.0) + (max_kw_words * 20.0) + float(max_kw_len)
                candidates.append((spec_score, rule, matched_keywords))

        if not candidates:
            return None

        # Sort candidates primarily by specificity score (descending), secondarily by rule confidence
        candidates.sort(key=lambda c: (c[0], c[1].confidence), reverse=True)
        best_score, best_rule, best_tokens = candidates[0]

        return (
            best_rule.category,
            best_rule.subcategory,
            best_rule.confidence,
            best_rule.rule_id,
            best_tokens,
        )


default_rule_engine = RuleEngine()
