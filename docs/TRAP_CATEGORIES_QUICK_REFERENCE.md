# CISSP Exam Trap Categories — Quick Reference Table

**Print this page and keep it at your desk during study sessions.**

---

## Core Categories (11 Original)

| Code | Category | The Trap | The Fix | Example |
|------|----------|----------|---------|---------|
| **NEG** | Negative Modifiers | Skim "NOT/LEAST/EXCEPT" → answer obvious positive | Circle negatives, flip the stem | Q: LEAST effective control? → Trap: Encryption ✗ → Correct: Backups ✓ |
| **ABS** | Absolute Language | Pick "Always/Never/All" because sounds confident | Eliminate absolute words immediately | Trap: "Completely prevent" ✗ → Correct: "Significantly reduce" ✓ |
| **ROLE** | Job Title Mismatch | Technical fix when role is non-technical (Manager, Owner) | Match role to authority level | Data Owner → Approve Policy ✓ (not Install DLP) |
| **ORDER** | Process Sequence | Jump to solution missing the mandatory first step | Memorize lifecycles (BCP, Incident, SDLC) | Incident first = Contain, not Eradicate ✓ |
| **SCOPE** | Boundary Confusion | Apply on-prem logic to cloud or miss responsibility | IaaS: You own OS/Apps. SaaS: You own Data/Access | Reconfigure guest OS (not hypervisor) ✓ |
| **ALL** | Umbrella Effect | Pick specific answer when broader one includes it | Ask: "Does this broader answer cover it?" | Defense-in-Depth ✓ (not just IDS) |
| **GOLD** | Shiny Object | Complex/crypto term looks impressive but irrelevant | Eliminate wrong domain | Identity proofing = OTP token ✓ (not AES encryption) |
| **ETHIC** | Moral Hazard | Pick vigilante option (hack back) or legal-only | ISC2 Canon: Society > Org > Auth > Actions | Isolate + preserve logs ✓ (not hack back) |
| **EASY** | Overthink | Assume simple question is a trick | Trust textbook answer when performing well | MFA = textbook answer ✓ (not retinal scan) |
| **TIME** | Clock Killer | Spend 4+ minutes on hard question | Eliminate 2 wrongs, guess, move on | 90-second rule per question ✓ |
| **REPEAT** | Deja Vu | Assume repeat topic = got it wrong before | Treat as new question, apply rules fresh | BCP question again = read fresh ✓ |

---

## Specialized Categories (10 Additional)

| Code | Category | The Trap | The Fix | Example |
|------|----------|----------|---------|---------|
| **COMPLIANCE** | Regulatory Confusion | Mix GDPR/CCPA/HIPAA/PCI/SOX/ISO 27001 | GDPR = EU data. CCPA = CA data. HIPAA = healthcare | EU customer = GDPR ✓ (not CCPA) |
| **HIERARCHY** | Authority Mismatch | Wrong person has decision authority | CEO = Budget. CISO = Strategy. Owner = Data decisions | Data Owner approves access ✓ (not CISO directly) |
| **TOOL** | Wrong Technology | Pick technically sound but suboptimal tool | Firewall ≠ insider threats. DLP = data theft | Stop insider theft = DLP ✓ (not firewall) |
| **CONTEXT** | Missing Scenario Clues | Miss critical detail: internal/external/regulated/startup | Highlight: Internal vs External, Cloud vs On-prem | Third-party cloud = shared model ✓ |
| **DEFINITION** | Concept Confusion | Confuse Authentication ≠ Authorization, Risk ≠ Threat | Create flashcards for similar pairs | Improve Authorization = RBAC ✓ (not 2FA) |
| **LIFECYCLE** | Process Stage Error | Right technique, wrong stage of lifecycle | BCP: BIA → Plan → Implement → Test → Maintain | First incident step = Contain ✓ (not eradicate) |
| **METRIC** | Measurement Mismatch | Pick important but irrelevant metric | RTO = recovery time. RPO = recovery point. SLA = uptime% | Measure DR = RTO/RPO ✓ (not SLA) |
| **ASSUMPTION** | Unstated Prerequisites | Answer only valid if unstated assumption true | Expect answers to work in edge cases too | Encrypt + verify cert ✓ (not just encrypt) |
| **VERSUS** | Similar Options | Both technically true, but one is BEST practice | Compare against ISC2 standards | 4096-bit RSA ✓ (better than 2048-bit) |
| **TIMING** | When vs What | Understand WHAT but miss WHEN in sequence | Create timeline diagrams for processes | Capture RAM first ✓ (not analyze first) |

---

## Study Priority Matrix

### 🔴 HIGH PRIORITY (Study 30+ hours)
**These appear in 35%+ of questions. Master these first.**

1. **NEG** (12%) — Negative modifiers appear in almost every exam section
2. **ORDER** (10%) — Every CISSP domain has process sequences
3. **TOOL** (10%) — Matching threats to security tools is critical
4. **ROLE** (11%) — ISC2 emphasizes responsibility alignment
5. **LIFECYCLE** (11%) — BCP, incident response, SDLC are foundational
6. **DEFINITION** (9%) — Concept clarity is essential for all domains
7. **COMPLIANCE** (8%) — Regulatory frameworks are heavily tested

### 🟡 MEDIUM PRIORITY (Study 15+ hours)
**These appear in 10-20% of questions. Study after high priority.**

8. **HIERARCHY** (7%) — Organizational structure matters
9. **SCOPE** (9%) — Cloud concepts increasingly tested
10. **ALL** (9%) — Strategic thinking vs tactical
11. **VERSUS** (8%) — Best practice selection
12. **ABS** (9%) — Eliminate absolute language
13. **CONTEXT** (6%) — Scenario awareness
14. **TIMING** (6%) — Sequence understanding

### 🟢 LOW PRIORITY (Study 5+ hours)
**These appear in <10% of questions. Polish your preparation.**

15. **GOLD** (9%) — Distraction elimination
16. **ETHIC** (8%) — ISC2 Code of Ethics
17. **EASY** (8%) — Confidence building
18. **TIME** (7%) — Time management tactics
19. **REPEAT** (7%) — CAT psychology
20. **METRIC** (5%) — Measurement precision
21. **ASSUMPTION** (5%) — Edge case thinking

---

## Quick Elimination Guide

**When stuck on a question, ask yourself:**

1. **Does the question have "NOT/LEAST/EXCEPT"?** → Check for NEG trap
2. **Does it say "Always/Never/All"?** → Check for ABS trap
3. **Does it mention a job title?** → Check for ROLE trap
4. **Does it ask for a first/initial step?** → Check for ORDER trap
5. **Does it mention cloud (IaaS/PaaS/SaaS)?** → Check for SCOPE trap
6. **Are there 2 similar-sounding answers?** → Check for VERSUS trap
7. **Does it mention regulatory (GDPR/HIPAA/PCI)?** → Check for COMPLIANCE trap
8. **Is the answer too technical/impressive?** → Check for GOLD trap
9. **Does it ask about a specific role's responsibility?** → Check for HIERARCHY trap
10. **Are you spending >90 seconds?** → TIME trap — move on

---

## Pre-Exam Checklist (Review 1 Hour Before CAT)

- [ ] Review HIGH PRIORITY categories (NEG, ORDER, TOOL, ROLE, LIFECYCLE, DEFINITION, COMPLIANCE)
- [ ] Read 3 examples from each category
- [ ] Practice 5-question drills with trap identification
- [ ] Review ISC2 process lifecycles
- [ ] Review organizational role matrix
- [ ] Verify you know regulatory framework differences
- [ ] Confirm you trust textbook answers
- [ ] Check your 90-second timer works

---

## During the CAT: The Trap Identification Flow

```
Read Question
    ↓
Identify domain/topic
    ↓
Look for trap indicators:
  - Negative words? (NEG)
  - Absolute words? (ABS)
  - Job title mentioned? (ROLE)
  - Process sequence? (ORDER)
  - Cloud model? (SCOPE)
  - Similar options? (VERSUS)
  - Regulatory mention? (COMPLIANCE)
    ↓
Re-read with trap in mind
    ↓
Eliminate 2 obvious wrongs
    ↓
Pick between remaining 2
    ↓
Move to next question (90-sec max)
```

---

## Category Color Code (For Study Materials)

- **RED (Highest Priority):** NEG, ORDER, TOOL, ROLE, LIFECYCLE, DEFINITION, COMPLIANCE
- **YELLOW (Medium Priority):** HIERARCHY, SCOPE, ALL, VERSUS, ABS, CONTEXT, TIMING
- **GREEN (Lower Priority):** GOLD, ETHIC, EASY, TIME, REPEAT, METRIC, ASSUMPTION

---

**Last Updated:** July 14, 2026  
**Version:** 1.0  
**Share with:** Study groups, practice test groups
