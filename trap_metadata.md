# CISSP Trap Framework - Complete Metadata Reference

**Version:** 2.0  
**Created:** 2026-07-13  
**Purpose:** Define trap codes, concept categories, and how to interpret them in student reports

---

## PART 1: TRAP CODE DEFINITIONS

### Category 1: END GAME TRAPS (Managerial/Business Perspective)
Think like a **CISO**, not a technician.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **MGT** | Managerial Mindset | Policy/Process vs. Technology | You picked "install X" instead of "draft policy" | Learn governance frameworks, policy creation |
| **BSC** | Business Continuity Choice | ALE Analysis vs. Quick Fix | You picked the technical solution without cost analysis | Study RTO, RPO, ALE calculations |
| **RFP** | Risk Framework Puzzle | Accept/Mitigate/Transfer/Avoid | You picked "firewall" when "insurance" was right | Know when each risk response applies |
| **ETH** | Ethical Fence | Ethics > Legal > Practical | You picked "hack back" instead of "protect society" | Study ISC2 Code of Ethics |
| **SLA** | Service Level Agreement | RTO/RPO Driven Response | You picked "restore" instead of "activate DR plan" | Understand SLA/RTO/RPO purpose |

### Category 2: BLIND SPOT TRAPS (Language Misses)
Your brain skips small words under exam stress.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **MOD** | Negative/Modifier | LEAST/EXCEPT/NOT/MOST | You read "LEAST" and picked the MOST effective | Read the last sentence TWICE |
| **ABS** | Absolute Language | Always/Never/All/Every | You picked an answer with "completely eliminate risk" | Learn: residual risk ALWAYS exists |
| **FAM** | False Assumption | Vendor Brand vs. Generic | You picked "Palo Alto" instead of "NGFW" | Use ISC2 glossary terms, not brand names |

### Category 3: ORDER OF OPERATIONS TRAPS (Process Sequence)
ISC2 is obsessed with the correct sequence.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **IRP** | Incident Response Process | Prep→Detect→Contain→Eradicate→Recover→Lessons | You picked "eradicate malware" as the FIRST step | Learn NIST IR phases in order |
| **BCP** | Business Continuity Plan | Initiation→BIA→Strategy→Approval→Test | You picked "write the plan" first instead of "BIA" | BIA comes before strategy design |
| **SDL** | SDLC Phases | Req→Design→Dev→Test→Impl | You picked "fix bug in production" | Changes require dev environment first |
| **FOR** | Forensics Order | Volatile (RAM) then Disk | You picked "shut down system" first | Capture RAM before disk (volatility order) |
| **ORD** | Process Sequence (General) | Order of any sequential process | You mixed up phases/steps | Identify the process, recall the order |

### Category 4: WHO OWNS IT? TRAPS (Scope & Boundaries)
Know responsibility/ownership boundaries.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **SCO** | Scope & Boundaries | Cloud Consumer vs. Provider | Encryption in IaaS (consumer) vs SaaS (provider) | Learn CSA cloud responsibility matrix |
| **RAC** | Role Confusion | Data Owner vs. Custodian vs. Admin | You picked "IT Admin" instead of "Business Manager" | Know who decides (Owner) vs. executes (Custodian) |
| **GEO** | Jurisdiction | GDPR/HIPAA/Local Law | You picked a technical control instead of "consult Legal" | Legal/compliance ALWAYS overrides technical |

### Category 5: READING COMPREHENSION TRAPS (Best Answer Distractors)
All answers are technically true—pick the BROADEST one.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **ALL** | Umbrella/All-of-the-Above | Pick the broadest answer | You picked Option A when Option C encompasses A+B | Look for "Defense in Depth," "risk management," etc. |
| **NON** | Non-sequitur/Shiny Object | Technically correct but wrong question | Question: Authentication, You picked: "AES-256 encryption" | Read question stem 3 times |
| **TIM** | Timeline Trick | Immediate vs. Long-term | You picked "update training" instead of "disconnect network" | For "FIRST/IMMEDIATE," pick containment, not prevention |

### Category 6: HUMAN FACTOR TRAPS (Soft Skills)
People > Technology in ISC2.

| Code | Name | Tests | Red Flag | Study Focus |
|------|------|-------|----------|-------------|
| **CUL** | Culture Shock | User Training vs. Technical Control | You picked "DLP software" instead of "awareness training" | Root cause is usually human behavior |

---

## PART 2: CONCEPT SUB-CATEGORIES

When a question doesn't fit trap codes above, it's categorized by the TYPE OF CONCEPT being tested.

| Code | Name | Tests | Example | Study Strategy |
|------|------|-------|---------|-----------------|
| **DEF_DIST** | Definition + Distinction | Know what X means AND how it differs from Y | Q4: MAD vs RTO/RPO | Create comparison tables (A vs B vs C) |
| **DEFINITION** | Pure Definition | Know the exact definition | Q7: "Policy is promulgated by senior management" | Memorize ISC2 glossary definitions |
| **PURPOSE** | Purpose/Use Case | Know WHEN and WHERE to use something | Q17: SLA for regularly recurring activities | Study use cases for each concept |
| **APPLICATION** | Scenario Application | Apply concept to a situation | Long scenario questions (>150 words) | Practice case studies, think like CISO |
| **RECALL** | Knowledge Recall | Simple factual knowledge | "Which law governs medical data?" | Flashcards, memorization |
| **COMPARISON** | Compare/Distinguish | Identify differences between concepts | "Difference between X and Y?" | Create Venn diagrams |
| **CALCULATION** | Math/Metrics | Compute a value or formula | ALE, RTO, risk score formulas | Work through examples step-by-step |
| **ACRONYM** | Multiple Acronyms | Distinguish similar acronyms | Question mentions 3+ acronyms | Acronym decoder sheet |
| **FRAMEWORK** | Framework/Model Knowledge | Know components/phases of a framework | SDLC phases, NIST CSF pillars | Learn the framework structure |
| **DISTINCTION** | Semantic Distinction | Distinguish similar-sounding concepts | Confidentiality vs. Integrity vs. Availability | Color code or use concept maps |

---

## PART 3: TRAP CODE CHEAT SHEET (What to Study)

### If you got it WRONG because of...

**MOD (Modifier)**: Read the question stem TWICE. Highlight "LEAST", "EXCEPT", "NOT", "MOST"

**ABS (Absolute)**: Remember: Absolutes are almost always WRONG in security. There's always residual risk.

**BEST**: Compare all options. Pick the most strategic, not just correct.

**ALL**: If three answers look good, pick the one that encompasses the others.

**MGT**: If it says "manager/director/policy" in stem, lean toward process/policy over technology.

**RAC**: Know the roles:
- **Data Owner** = Business unit (decides access)
- **Data Custodian** = IT (implements/executes)
- **Security Admin** = Operates controls

**SCO (Cloud Scope)**:
- IaaS: Consumer responsible for OS, apps, data, access
- PaaS: Consumer responsible for apps, data, access
- SaaS: Provider responsible for everything

**IRP (Incident Response)**: When in doubt on first step:
1. **Detect** → 2. **Contain** → 3. **Eradicate** → 4. **Recover**

**BCP (Business Continuity)**: Always start with **Business Impact Analysis (BIA)** to identify critical functions.

**ETH (Ethics)**: ISC2 Code of Ethics = **Protect society > follow law > protect employer**.

**TIM (Timeline)**: FIRST/IMMEDIATE action = containment/isolation, NOT long-term prevention.

---

## PART 4: REPORT INTERPRETATION GUIDE

### What trap codes mean in YOUR student reports:

```
Trap Code Present → Meaning for Student
─────────────────────────────────────────────
MGT + WRONG    → "You picked technical, needed strategic"
MOD + WRONG    → "You missed a key word (NOT/LEAST/EXCEPT)"
ALL + WRONG    → "You picked partial answer, needed umbrella answer"
RAC + WRONG    → "You confused roles/responsibilities"
IRP + WRONG    → "You mixed up incident response phases"
DEF_DIST + WRONG → "You know the term but not how it differs from similar terms"
```

### Study Priority by Trap:

| Priority | Trap(s) | Why | Action |
|----------|---------|-----|--------|
| **🔴 CRITICAL** | MOD, MGT, IRP, BCP, ETH | These are objective rules, not opinion | Memorize and practice |
| **🟡 HIGH** | ALL, DEF_DIST, RAC, SCO | These are common confusion points | Make comparison charts |
| **🟢 MEDIUM** | BEST, ABS, CALCULATION | These require strategy/math skills | Practice with explanations |
| **🔵 LOW** | ACRONYM, FRAMEWORK, RECALL | These are pure memorization | Flashcards |

---

## PART 5: SAMPLE REPORT OUTPUT

### How trap codes appear in Q&A Breakdown sheet:

```
Q# | Question Type | Trap Code | Your Ans | Correct | Result  | Notes
───┼───────────────┼──────────┼─────────┼─────────┼────────┼──────────────
 4 | Application   | DEF_DIST | A       | C       | ✗ WRONG| Confused MAD with RTO
17 | Application   | PURPOSE  | A       | B       | ✗ WRONG| Didn't understand SLA use case
23 | Application   | MGT      | D       | A       | ✗ WRONG| Picked technical, needed policy
45 | Scenario      | BEST     | C       | A       | ✗ WRONG| Picked good answer, needed best
89 | Application   | IRP      | D       | B       | ✗ WRONG| Wrong IR phase order
```

---

## PART 6: CUSTOM RECOMMENDATIONS BY TRAP

### If your student got 3+ questions WRONG in the same trap:

| Trap | Root Cause | Recommended Study |
|------|------------|-------------------|
| **MOD** | Test anxiety → brain skips words | Use highlighter on question stem during practice |
| **MGT** | Too technical mindset | Study Business Continuity, Risk Management, Governance domains |
| **BEST** | Settles for "correct" instead of "optimal" | Practice: always rank all 4 options by quality |
| **DEF_DIST** | Memorizes definition, not context | Create comparison matrix: Term A vs Term B vs Term C |
| **IRP/BCP** | Confuses similar processes | Draw flowcharts of each phase, laminate and review |
| **RAC** | Mixes up roles | Memorize: Owner (decide) vs Custodian (execute) vs Admin (operate) |
| **ALL** | Overthinks, misses umbrella | Practice identifying "umbrella" answers: "Defense in Depth," "Risk Management," etc. |

---

## PART 7: QUICK REFERENCE - AT THE EXAM

**Read the question stem LAST SENTENCE first to identify:**
1. The ROLE (analyst? manager? auditor?)
2. The ACTION WORD (BEST? FIRST? LEAST? MOST?)

Then:
- ✗ Eliminate answers with absolute language ("completely," "always," "never")
- ✗ Eliminate technical answers if stem says "policy/manager/process"
- ✗ Eliminate partial answers if broader option exists
- ✓ Pick the answer that fits the role + action word + strategy level

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Initial | Basic trap codes |
| 2.0 | 2026-07-13 | Added concept categories, metadata, study guides |

---

**Last Updated:** 2026-07-13  
**Maintained by:** CISSP Analyzer System  
**Questions?** Review examples for each trap code above.
