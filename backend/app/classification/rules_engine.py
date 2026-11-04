"""Deterministic rule engine with keyword inverted index."""

import re
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class ClassificationRule(BaseModel):
    """Deterministic classification rule definition."""

    rule_id: str
    category: str
    subcategory: Optional[str] = None
    keywords: List[str]
    direction: str = "both"  # "debit", "credit", or "both"
    priority: int = 10       # Higher number = higher precedence
    confidence: float = 0.95


# Seed list of deterministic keyword rules covering AU, UK, and universal patterns
DEFAULT_RULES: List[ClassificationRule] = [
    # Salary & Wages
    ClassificationRule(
        rule_id="RULE_SALARY_01",
        category="Salary & Wages",
        subcategory="Regular Pay",
        keywords=["SALARY", "PAYROLL", "WAGES", "DIRECT CREDIT PAY", "EMPLOYER PAY"],
        direction="credit",
        priority=20,
        confidence=0.98,
    ),
    # Groceries (AU & UK)
    ClassificationRule(
        rule_id="RULE_GROC_AU_01",
        category="Groceries",
        subcategory="Supermarket",
        keywords=["WOOLWORTHS", "COLES", "ALDI", "IGA SUPERMARKET", "HARRIS FARM"],
        direction="debit",
        priority=15,
        confidence=0.98,
    ),
    ClassificationRule(
        rule_id="RULE_GROC_UK_01",
        category="Groceries",
        subcategory="Supermarket",
        keywords=["TESCO", "SAINSBURYS", "ASDA", "MORRISONS", "WAITROSE", "CO-OP FOOD", "LIDL"],
        direction="debit",
        priority=15,
        confidence=0.98,
    ),
    # Utilities & Bills
    ClassificationRule(
        rule_id="RULE_UTIL_AU_01",
        category="Utilities & Bills",
        subcategory="Internet & Mobile",
        keywords=["TELSTRA", "OPTUS", "VODAFONE", "TPG INTERNET", "AUSSIE BROADBAND", "BELONG"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_AU_02",
        category="Utilities & Bills",
        subcategory="Electricity & Gas",
        keywords=["AGL ENERGY", "ORIGIN ENERGY", "ENERGYAUSTRALIA", "SYDNEY WATER", "YARRA VALLEY WATER"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_UK_01",
        category="Utilities & Bills",
        subcategory="Electricity & Gas",
        keywords=["BRITISH GAS", "EDF ENERGY", "E.ON", "OCTOPUS ENERGY", "THAMES WATER", "SEVERN TRENT"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_UTIL_UK_02",
        category="Utilities & Bills",
        subcategory="Internet & Mobile",
        keywords=["EE MOBILE", "O2 UK", "THREE UK", "BT BILL", "SKY DIGITAL", "VIRGIN MEDIA"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    # Transport & Travel (AU & UK)
    ClassificationRule(
        rule_id="RULE_TRANS_AU_01",
        category="Transport & Travel",
        subcategory="Tolls",
        keywords=["LINKT", "TRANSURBAN", "EASTLINK", "ROADS AND MARITIME", "TOLL"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    ClassificationRule(
        rule_id="RULE_TRANS_AU_02",
        category="Transport & Travel",
        subcategory="Fuel",
        keywords=["AMPOL", "CALTEX", "BP CONNECT", "7-ELEVEN FUEL", "UNITED PETROLEUM"],
        direction="debit",
        priority=12,
        confidence=0.90,
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
    ClassificationRule(
        rule_id="RULE_TRANS_UNI_01",
        category="Transport & Travel",
        subcategory="Rideshare & Taxi",
        keywords=["UBER TRIP", "UBER *TRIP", "DIDI", "OLA", "CABCHARGE"],
        direction="debit",
        priority=15,
        confidence=0.95,
    ),
    # Dining & Restaurants
    ClassificationRule(
        rule_id="RULE_DINE_01",
        category="Dining & Restaurants",
        subcategory="Cafes & Coffee",
        keywords=["STARBUCKS", "COSTA COFFEE", "PRET A MANGER", "GREGGS", "NERO", "BOOST JUICE"],
        direction="debit",
        priority=12,
        confidence=0.92,
    ),
    ClassificationRule(
        rule_id="RULE_DINE_02",
        category="Dining & Restaurants",
        subcategory="Takeaway & Delivery",
        keywords=["MCDONALDS", "HUNGRY JACKS", "KFC", "SUBWAY", "UBER EATS", "DELIVEROO", "DOORDASH", "JUST EAT"],
        direction="debit",
        priority=14,
        confidence=0.95,
    ),
    # Shopping & Retail
    ClassificationRule(
        rule_id="RULE_SHOP_AU_01",
        category="Shopping & Retail",
        subcategory="Home & Hardware",
        keywords=["BUNNINGS", "KMART", "TARGET", "BIG W", "JB HI-FI", "OFFICEWORKS", "MYER"],
        direction="debit",
        priority=12,
        confidence=0.92,
    ),
    ClassificationRule(
        rule_id="RULE_SHOP_UK_01",
        category="Shopping & Retail",
        subcategory="Clothing",
        keywords=["MARKS AND SPENCER", "PRIMARK", "NEXT RETAIL", "JOHN LEWIS", "ARGOS", "CURRYS"],
        direction="debit",
        priority=12,
        confidence=0.92,
    ),
    ClassificationRule(
        rule_id="RULE_SHOP_UNI_01",
        category="Shopping & Retail",
        subcategory="Online Shopping",
        keywords=["AMAZON", "EBAY", "PAYPAL", "APPLE.COM", "GOOGLE *STORE"],
        direction="debit",
        priority=10,
        confidence=0.90,
    ),
    # Healthcare & Pharmacy
    ClassificationRule(
        rule_id="RULE_HEALTH_01",
        category="Healthcare & Pharmacy",
        subcategory="Pharmacy",
        keywords=["CHEMIST WAREHOUSE", "PRICELINE", "BOOTS PHARMACY", "SUPERDRUG", "PHARMACY", "MEDICAL CENTRE"],
        direction="debit",
        priority=14,
        confidence=0.95,
    ),
    # Entertainment & Subscriptions
    ClassificationRule(
        rule_id="RULE_ENT_01",
        category="Entertainment & Subscriptions",
        subcategory="Streaming Services",
        keywords=["NETFLIX", "SPOTIFY", "DISNEY PLUS", "DISNEY+", "YOUTUBE PREMIUM", "APPLE MUSIC", "AUDIBLE"],
        direction="debit",
        priority=16,
        confidence=0.98,
    ),
    # Bank Fees & Charges
    ClassificationRule(
        rule_id="RULE_FEES_01",
        category="Fees & Charges",
        subcategory="Bank Fees",
        keywords=["ACCOUNT FEE", "MONTHLY FEE", "OVERDRAWN FEE", "OVERDRAFT INTEREST", "INTERNATIONAL TRANSACTION FEE", "LATE PAYMENT FEE"],
        direction="debit",
        priority=18,
        confidence=0.98,
    ),
    # Cash Withdrawal
    ClassificationRule(
        rule_id="RULE_CASH_01",
        category="Cash Withdrawal",
        subcategory="ATM Withdrawal",
        keywords=["ATM WITHDRAWAL", "ATM WDL", "CASH WITHDRAWAL", "BRANCH CASH WDL"],
        direction="debit",
        priority=20,
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
]


class RuleEngine:
    """Fast deterministic rule engine using token matching."""

    def __init__(self, rules: Optional[List[ClassificationRule]] = None):
        self.rules = sorted(rules or DEFAULT_RULES, key=lambda r: r.priority, reverse=True)

    def classify(
        self, description: str, direction: str = "debit"
    ) -> Optional[Tuple[str, Optional[str], float, str, List[str]]]:
        """Match description against rules. Returns (category, subcategory, confidence, rule_id, matched_tokens)."""
        upper_desc = description.upper()

        for rule in self.rules:
            # Check direction constraint if specified
            if rule.direction != "both" and direction != "both":
                if rule.direction != direction:
                    continue

            matched_keywords: List[str] = []
            for kw in rule.keywords:
                # Use regex word boundary check where possible
                escaped = re.escape(kw)
                if re.search(rf"\b{escaped}\b", upper_desc):
                    matched_keywords.append(kw)

            if matched_keywords:
                return (
                    rule.category,
                    rule.subcategory,
                    rule.confidence,
                    rule.rule_id,
                    matched_keywords,
                )

        return None


default_rule_engine = RuleEngine()
