#!/usr/bin/env python3
"""
CISSP Exam Trap Framework
Categorizes tricks based on cognitive biases and structural traps

Framework by: ISC2 Analysis
Implementation: CISSP Analyzer v2.0
"""

# ============================================================================
# TRAP CATEGORIES & CODES
# ============================================================================

TRAP_CATEGORIES = {
    # 1. END GAME TRAPS (Business/Managerial Perspective)
    "BSC": {
        "name": "Business Continuity Choice",
        "category": "End Game Traps",
        "description": "Profit vs. Security - ALE analysis vs. quick technical fix",
        "example": "Did you pick 'fix the vulnerability' instead of 'calculate ALE'?"
    },
    "ETH": {
        "name": "Ethical Fence",
        "category": "End Game Traps",
        "description": "Legal vs. Ethical vs. Practical - ISC2 Code of Ethics",
        "example": "Did you pick 'hack back' instead of 'protect society first'?"
    },
    "RFP": {
        "name": "Risk Framework Puzzle",
        "category": "End Game Traps",
        "description": "Accept vs. Mitigate vs. Transfer vs. Avoid",
        "example": "Did you pick 'firewall' (Mitigate) instead of 'insurance' (Transfer)?"
    },
    "SLA": {
        "name": "Service Level Agreement",
        "category": "End Game Traps",
        "description": "Reactive vs. Proactive - RTO/RPO driven",
        "example": "Did you pick 'restore' instead of 'activate DR plan'?"
    },

    # 2. BLIND SPOT TRAPS (Language & Modifiers)
    "MOD": {
        "name": "Negative/Modifier",
        "category": "Blind Spot Traps",
        "description": "LEAST, EXCEPT, NOT, MOST - missed negation",
        "example": "Did you read 'LEAST effective' and pick the MOST effective?"
    },
    "ABS": {
        "name": "Absolute Language",
        "category": "Blind Spot Traps",
        "description": "Always, Never, All, Every - absolutes are usually wrong",
        "example": "Did you pick 'completely eliminate risk'? (Trick: residual risk exists)"
    },
    "FAM": {
        "name": "False Assumption/Jargon",
        "category": "Blind Spot Traps",
        "description": "Vendor brand vs. generic term - pick generic/official",
        "example": "Did you pick 'Palo Alto firewall' instead of 'NGFW'?"
    },

    # 3. ORDER OF OPERATIONS TRAPS (Process Sequence)
    "IRP": {
        "name": "Incident Response Process",
        "category": "Order of Operations",
        "description": "Prep→Detect→Contain→Eradicate→Recover→Lessons",
        "example": "Did you pick 'eradicate' instead of 'contain' as FIRST step?"
    },
    "BCP": {
        "name": "Business Continuity Plan",
        "category": "Order of Operations",
        "description": "Initiation→BIA→Strategies→Approval→Testing",
        "example": "Did you pick 'write plan' instead of 'conduct BIA' first?"
    },
    "FOR": {
        "name": "Forensics Order",
        "category": "Order of Operations",
        "description": "Capture volatile memory first, then disk",
        "example": "Did you pick 'shut down system' instead of 'capture RAM'?"
    },
    "SDL": {
        "name": "SDLC Phases",
        "category": "Order of Operations",
        "description": "Req→Design→Dev→Test→Impl - separation of duties",
        "example": "Did you pick 'fix in production' instead of 'change request'?"
    },
    "ORD": {
        "name": "Process Sequence",
        "category": "Order of Operations",
        "description": "General process/phase ordering confusion",
        "example": "Did you mix up the order of any process steps?"
    },

    # 4. WHO OWNS IT? TRAPS (Scope & Boundaries)
    "SCO": {
        "name": "Scope & Boundaries",
        "category": "Scope Traps",
        "description": "Cloud Consumer vs. Provider (CCSP responsibility)",
        "example": "Did you forget encryption is Consumer's job in IaaS but Provider's in SaaS?"
    },
    "RAC": {
        "name": "Role Confusion",
        "category": "Scope Traps",
        "description": "Data Owner vs. Custodian vs. Admin",
        "example": "Did you pick 'IT Admin' instead of 'Business Manager' for authorization?"
    },
    "GEO": {
        "name": "Jurisdiction",
        "category": "Scope Traps",
        "description": "GDPR, HIPAA, Privacy Laws - legal > technical",
        "example": "Did you pick technical control instead of 'consult Legal'?"
    },

    # 5. READING COMPREHENSION TRAPS (Best Answer Distractors)
    "ALL": {
        "name": "All-of-the-Above/Umbrella",
        "category": "Reading Comprehension",
        "description": "All answers true - pick the broadest umbrella answer",
        "example": "Is the answer 'Defense in Depth' because it includes firewall AND IDS?"
    },
    "NON": {
        "name": "Non-sequitur / Shiny Object",
        "category": "Reading Comprehension",
        "description": "Technically correct but answers wrong question",
        "example": "Question asks Authentication, you picked 'AES-256' (Confidentiality)?"
    },
    "TIM": {
        "name": "Timeline Trick",
        "category": "Reading Comprehension",
        "description": "Immediate response vs. long-term fix",
        "example": "Did you pick 'update training' instead of 'disconnect network'?"
    },

    # 6. HUMAN FACTOR TRAPS (Soft Skills)
    "MGT": {
        "name": "Managerial Mindset",
        "category": "Human Factor",
        "description": "Policy vs. Procedure vs. Guideline - CISO thinking",
        "example": "Did you pick 'install antivirus' instead of 'draft policy'?"
    },
    "CUL": {
        "name": "Culture Shock",
        "category": "Human Factor",
        "description": "User training vs. technical control - people > technology",
        "example": "Did you pick 'DLP software' instead of 'awareness training'?"
    },

    # 7. CAT FORMAT META-TRICKS
    "TMI": {
        "name": "Too Much Info",
        "category": "Meta-Tricks",
        "description": "Overthinking easy questions in CAT format",
        "example": "Is the first question so easy you're second-guessing yourself?"
    },
    "BFT": {
        "name": "Bait & Switch",
        "category": "Meta-Tricks",
        "description": "Match role in stem - analyst=technical, manager=policy",
        "example": "Did you pick policy when stem said 'as a security analyst'?"
    },
}

# ============================================================================
# QUICK REFERENCE PATTERNS
# ============================================================================

TRAP_TRIGGERS = {
    # Keywords that trigger specific traps
    "MOD": ["NOT", "EXCEPT", "LEAST", "NEVER", "ONLY"],
    "ALL": ["ALL", "UMBRELLA", "ENCOMPASSES", "INCLUDES ALL"],
    "MGT": ["POLICY", "PROCESS", "PROCEDURE", "MANAGER", "DIRECTOR"],
    "BCP": ["BCP", "BUSINESS CONTINUITY", "PHASE"],
    "IRP": ["INCIDENT RESPONSE", "FIRST STEP", "DETECT", "CONTAIN"],
    "SDL": ["SDLC", "DEVELOPMENT", "TESTING", "PHASE"],
    "SCO": ["CLOUD", "CONSUMER", "PROVIDER", "RESPONSIBILITY"],
    "TIM": ["IMMEDIATE", "FIRST", "SHORT-TERM", "LONG-TERM"],
    "BFT": ["AS A", "SECURITY ANALYST", "SECURITY MANAGER", "CISO"],
}

# ============================================================================
# TRAP ASSIGNMENT LOGIC
# ============================================================================

def identify_trap_code(question_text: str, explanation: str, options: dict = None) -> list:
    """
    Identify which trap code(s) apply to a question

    Args:
        question_text: The full question stem
        explanation: The official explanation/answer rationale
        options: Dict of {letter: text} for all answer options

    Returns:
        List of trap codes that apply (primary first)
    """
    traps = []
    q_lower = question_text.lower()
    exp_lower = explanation.lower()

    # 1. Check for negative/modifier words
    if any(word in q_lower for word in TRAP_TRIGGERS["MOD"]):
        traps.append("MOD")

    # 2. Check for absolute language
    if any(word in q_lower for word in ["always", "never", "all", "every", "completely"]):
        traps.append("ABS")

    # 3. Check for process/order keywords
    if any(phrase in q_lower for phrase in ["bcp", "business continuity"]):
        traps.append("BCP")
    elif any(phrase in q_lower for phrase in ["incident response", "first step"]):
        traps.append("IRP")
    elif any(phrase in q_lower for phrase in ["sdlc", "development phase"]):
        traps.append("SDL")
    else:
        for keyword in ["phase", "step", "sequence", "order"]:
            if keyword in q_lower and "ORD" not in traps:
                traps.append("ORD")
                break

    # 4. Check for scope/boundaries keywords
    if any(word in q_lower for word in ["cloud", "consumer", "provider"]):
        traps.append("SCO")
    elif any(word in q_lower for word in ["owner", "custodian", "admin", "role"]):
        traps.append("RAC")
    elif any(word in q_lower for word in ["gdpr", "hipaa", "law", "jurisdiction", "compliance"]):
        traps.append("GEO")

    # 5. Check for managerial keywords
    if any(word in q_lower for word in TRAP_TRIGGERS["MGT"]):
        traps.append("MGT")
    elif "training" in q_lower or "awareness" in q_lower:
        traps.append("CUL")

    # 6. Check for best/primary
    if "best" in q_lower or "primary" in q_lower or "most" in q_lower:
        if "umbrella" in exp_lower or "encompasses" in exp_lower:
            traps.insert(0, "ALL")
        else:
            traps.append("BEST")

    # 7. Check for timeline
    if "immediate" in q_lower or "first" in q_lower:
        traps.append("TIM")

    # 8. Check for risk framework
    if "risk" in q_lower and any(word in q_lower for word in ["accept", "mitigate", "transfer", "avoid"]):
        traps.append("RFP")

    # 9. Check for SLA
    if "sla" in q_lower or "service level" in q_lower:
        traps.append("SLA")

    # 10. Check for ethical/legal
    if "ethic" in q_lower or "legal" in q_lower:
        traps.append("ETH")

    # Default if no specific trap found
    if not traps:
        traps.append("CONCEPT")

    return traps


# ============================================================================
# EXPORT
# ============================================================================

def get_trap_description(trap_code: str) -> dict:
    """Get full description of a trap code"""
    return TRAP_CATEGORIES.get(trap_code, {"name": "Unknown", "description": "No description"})


if __name__ == "__main__":
    # Test
    print("CISSP Trap Framework Loaded")
    print(f"Total Trap Codes: {len(TRAP_CATEGORIES)}")

    # Show all traps
    for code, data in sorted(TRAP_CATEGORIES.items()):
        print(f"  {code}: {data['name']}")
