# Dual-Tier System Examples: Real CISSP Questions from PDF

**Source:** CISSP Practice Assessment (Pages 21-45, Questions 77-162)  
**Demonstrating:** How TIER 1 + TIER 2 work together on actual exam questions

---

## Example 1: NEG Trap (Question 77)

### The Question
**Q77:** "A rogue wireless device has been found on a network, and the way it was discovered is that individuals were not able to get a DHCP address. **What should be done to prevent this in the future?**"

**Options:**
- A. **Turn on port authentication** on the host switches
- B. Create reservation on the DHCP server
- C. Set the clients to Bootstrap Protocol (BootP)
- D. Expand the reservation pool on the DHCP server

**Correct Answer:** A

### TIER 1 Analysis: What is Being Tested?
```json
{
  "domain": 3,
  "domain_name": "Security Architecture and Engineering",
  "topic": "Network Security",
  "difficulty": "Medium",
  "question_type": "Application",
  "exam_trick": "BEST"
}
```
✓ This tests your knowledge of network access control

### TIER 2 Analysis: How Does It Trick You?
```json
{
  "trap_codes": ["NEG"],
  "trap_details": {
    "NEG": {
      "name": "Negative Modifiers",
      "risk": "CRITICAL",
      "keywords_found": ["not"],
      "explanation": "Question starts with 'were not able' — tests if you misread or overthink"
    }
  },
  "risk_level": "CRITICAL"
}
```

### The Trap 🎯
- **Trap Type:** NEG (Negative Modifiers)
- **The Trick:** The word "NOT" in "were not able" might confuse you into picking an answer that ENABLES DHCP rather than PREVENTS rogue devices
- **Common Wrong Answer:** B (Create reservation on DHCP) — makes DHCP work, not blocks rogues
- **How to Avoid:** Read carefully: "prevent this in the future" means BLOCK, not enable

### ISC2 Fix
✓ Flip the stem: "...to PREVENT rogue devices" = Need access control (port authentication)  
✓ Answer A is correct because port authentication blocks unauthorized MAC addresses

---

## Example 2: TIME Trap (Question 79)

### The Question
**Q79:** "Your organization must still manage a Multiprotocol Label Switching (MPLS) network while converting their internal network system to SDN. **You want to have a better understanding of your prioritized traffic flows on the MPLS to match your SDN design.** What field in the header will provide the information of a MPLS label?"

**Options:**
- A. Stack
- B. TTL
- C. **Class of Service**
- D. QoS Bit

**Correct Answer:** C

### TIER 1 Analysis: What is Being Tested?
```json
{
  "domain": 3,
  "domain_name": "Security Architecture and Engineering",
  "topic": "Network Architecture",
  "difficulty": "Hard",
  "question_type": "Application",
  "exam_trick": "BEST"
}
```
✓ This tests specialized networking knowledge (MPLS, CoS)

### TIER 2 Analysis: How Does It Trick You?
```json
{
  "trap_codes": ["TIME", "REPEAT"],
  "trap_details": {
    "TIME": {
      "name": "Clock Killer",
      "risk": "CRITICAL",
      "reason": "Long complex scenario (350+ chars with technical jargon)",
      "explanation": "Takes 3-4 minutes to parse; if on exam early, you fall behind"
    },
    "REPEAT": {
      "name": "Deja Vu",
      "risk": "MEDIUM",
      "reason": "Domain 3 (network security) already seen before",
      "explanation": "May lead to assumption you got prior domain question wrong"
    }
  },
  "risk_level": "CRITICAL"
}
```

### The Trap 🎯
- **Trap Type:** TIME (Clock Killer)
- **The Trick:** Long scenario with technical jargon (MPLS, SDN, prioritized flows, header fields) that takes 4+ minutes to comprehend
- **Exam Impact:** On a 5.5-hour exam with 175 questions, losing 4 minutes here means you fall behind and rush later questions
- **Common Wrong Answer:** A (Stack) — technically part of MPLS but not what defines prioritization

### ISC2 Fix
✓ Skim quickly: "prioritized traffic flows" = need prioritization field = Class of Service  
✓ Don't get bogged down in MPLS technical details; focus on the question goal  
✓ If unsure after 2 minutes: guess C (CoS) and move on; don't spend 4 minutes

---

## Example 3: ROLE Trap (Question 85)

### The Question
**Q85:** "Which of the following could represent an identity management risk? A. **Provisioning a third-party identity as a service (IDaaS) without a proper SOC 2 report** providing an opinion of the organization's management of the trust principles."

**Options:**
- A. ✓ Provisioning IDaaS without SOC 2 audit
- B. Using Kerberos as single-sign-on
- C. Reviewing business policy before choosing solution
- D. Curtailing logging during non-business hours

**Correct Answer:** A

### TIER 1 Analysis: What is Being Tested?
```json
{
  "domain": 5,
  "domain_name": "Identity & Access Management",
  "topic": "Identity Management Risk",
  "difficulty": "Medium",
  "question_type": "Knowledge",
  "exam_trick": "BEST"
}
```
✓ Tests knowledge of third-party vendor risk assessment

### TIER 2 Analysis: How Does It Trick You?
```json
{
  "trap_codes": ["ROLE"],
  "trap_details": {
    "ROLE": {
      "name": "Job Title Mismatch",
      "risk": "HIGH",
      "detected": true,
      "explanation": "Question doesn't name a specific role, but assumes you understand RISK MANAGER perspective (auditing third parties)",
      "trap_content": "Options B, C, D all SEEM correct because they're identity management activities"
    }
  },
  "risk_level": "HIGH"
}
```

### The Trap 🎯
- **Trap Type:** ROLE (Job Title Mismatch)
- **The Trick:** All four options sound like identity management activities. The question asks which is a RISK, not which is correct practice.
- **Common Wrong Answer:** C (Reviewing business policy) — this IS correct practice, not a risk
- **Role Confusion:** Question assumes you're thinking like a SECURITY/RISK MANAGER (who audits vendors), not an IMPLEMENTER (who implements controls)

### ISC2 Fix
✓ Understand your role: "risk" questions test if you can IDENTIFY problems  
✓ Answer A: "without proper audit" = risk ✓  
✓ Answer C: "reviewing policy" = best practice, NOT a risk ✗  
✓ Match role to question type: "risk" = identify gaps; "procedure" = identify steps

---

## Example 4: ORDER Trap (Question 1 - Scenario)

### The Question (Hypothetical Composite)
**Q?:** "Which is the **FIRST step** in business continuity planning?"

**Options:**
- A. Conduct Business Impact Analysis (BIA)
- B. Develop the BCP document
- C. Activate the warm site
- D. Test recovery procedures

**Correct Answer:** A

### TIER 1 Analysis: What is Being Tested?
```json
{
  "domain": 1,
  "domain_name": "Security & Risk Management",
  "topic": "Business Continuity Planning",
  "difficulty": "Medium",
  "question_type": "Knowledge",
  "exam_trick": "FIRST"
}
```
✓ Tests knowledge of BCP lifecycle sequence

### TIER 2 Analysis: How Does It Trick You?
```json
{
  "trap_codes": ["ORDER", "ABS"],
  "trap_details": {
    "ORDER": {
      "name": "Process Sequence",
      "risk": "CRITICAL",
      "detected": true,
      "keywords_found": ["FIRST"],
      "explanation": "Key word FIRST demands understanding of mandatory sequence"
    },
    "ABS": {
      "name": "Absolute Language",
      "risk": "HIGH",
      "detected": true,
      "keywords_found": ["FIRST"],
      "explanation": "FIRST is absolute — must be step 1, not just important"
    }
  },
  "risk_level": "CRITICAL"
}
```

### The Trap 🎯
- **Trap Type:** ORDER (Process Sequence)
- **The Trick:** People know BCP is important but skip the FIRST step (BIA)
- **Common Wrong Answer:** B (Develop BCP) — sounds like the "main" activity, but it's step 2
- **ISC2 Lifecycle:** BIA → Plan → Test → Maintain (this is the ONLY correct order)

### ISC2 Fix
✓ Before answering ANY sequence question, recite the ISC2 lifecycle in order  
✓ BCP Lifecycle: **BIA first** (analyze impact) → Plan (create document) → Test → Execute  
✓ This is non-negotiable; it's the foundation of all contingency planning

---

## Example 5: SCOPE Trap (Question 95)

### The Question
**Q95:** "An organization has various forms of intellectual property labeled as confidential trade secrets... **Which access control methodology best fits the organization need?**"

**Options:**
- A. Rule-based access control (RBAC)
- B. Attribute-based access control (ABAC)
- C. Role-based access control (RBAC)
- D. Discretionary access control (DAC)

**Correct Answer:** B

### TIER 1 Analysis: What is Being Tested?
```json
{
  "domain": 5,
  "domain_name": "Identity & Access Management",
  "topic": "Access Control Models",
  "difficulty": "Medium",
  "question_type": "Application",
  "exam_trick": "BEST"
}
```
✓ Tests understanding of when to use ABAC vs RBAC vs DAC

### TIER 2 Analysis: How Does It Trick You?
```json
{
  "trap_codes": ["SCOPE", "ALL"],
  "trap_details": {
    "SCOPE": {
      "name": "Boundary Confusion",
      "risk": "HIGH",
      "detected": true,
      "explanation": "Scenario mentions: traditional groups (RBAC), specific conditions (ABAC), individual owners (DAC) — tests if you understand model boundaries",
      "correct_boundary": "ABAC includes all three (role + conditions + discretion)"
    },
    "ALL": {
      "name": "Umbrella Effect",
      "risk": "MEDIUM",
      "detected": true,
      "explanation": "Multiple correct answers (A/C/D) all fit SOME aspects; only B encompasses all"
    }
  },
  "risk_level": "HIGH"
}
```

### The Trap 🎯
- **Trap Type:** SCOPE (Boundary Confusion) + ALL (Umbrella Effect)
- **The Trick:** All four options ARE valid access control models, but only ABAC integrates all three requirements
- **Common Wrong Answer:** C (RBAC) — covers traditional groups but misses time-based/location-based conditions
- **Model Confusion:** Students pick tactical answers instead of strategic umbrella

### ISC2 Fix
✓ Understand model scope:
   - **RBAC:** Groups only (narrow) ✗
   - **DAC:** Individual owner discretion only (narrow) ✗
   - **MAC:** Mandatory classification (not flexible enough) ✗
   - **ABAC:** Role + Attributes + Conditions + Discretion (broad) ✓

---

## Quick Reference: Using Both Tiers Together

### Decision Tree: How to Answer CISSP Questions

```
QUESTION APPEARS
    ↓
[TIER 1] Read carefully — what domain/topic?
    ├─ Domain 1? → Study BCP/DRP concepts
    ├─ Domain 5? → Study IAM concepts
    └─ Other? → Know your domain first
    ↓
[TIER 2] Scan for trap keywords
    ├─ See "NOT/EXCEPT"? → NEG trap (flip stem)
    ├─ See "ALWAYS/NEVER"? → ABS trap (eliminate)
    ├─ See "FIRST/BEFORE"? → ORDER trap (know sequence)
    ├─ See job title? → ROLE trap (match role to answer)
    ├─ Question > 300 chars? → TIME trap (skim quickly)
    └─ Same domain as before? → REPEAT trap (don't second-guess)
    ↓
[ANSWER] Pick based on TIER 1 + TIER 2 insights
    ├─ TIER 1 narrows to 2-3 options
    ├─ TIER 2 eliminates trap answers
    └─ Choose remaining option with confidence
```

---

## Statistics: Trap Frequency in PDF Sample

| Trap Code | Count | Frequency | Strategy |
|-----------|-------|-----------|----------|
| **REPEAT** | 85 | 98.8% | Treat each domain fresh; don't assume prior was wrong |
| **NEG** | 22 | 25.6% | Practice flipping stems; this is a common trick |
| **TIME** | 4 | 4.7% | Set 2-minute timer; if unsure by then, guess and move |
| **ETHIC** | 3 | 3.5% | Know ISC2 Canon; eliminate offensive options |
| **ORDER** | 3 | 3.5% | Memorize ISC2 lifecycles (BCP, IR, SDLC, Forensics) |
| **ABS** | 3 | 3.5% | Eliminate 100% certainty; security is probabilistic |
| **ROLE** | 2 | 2.3% | Match job titles to functions (analyst/mgr/owner) |
| **ALL** | 2 | 2.3% | Pick strategic umbrella, not tactical detail |
| **SCOPE** | 1 | 1.2% | Know cloud responsibility model (IaaS/PaaS/SaaS) |
| **GOLD** | 1 | 1.2% | Irrelevant crypto rarely correct; match domain |

---

## Conclusion

The dual-tier system catches traps by:

1. **TIER 1** → Ensures you know the content
2. **TIER 2** → Teaches you to recognize ISC2's trick patterns

Together they create **exam-ready thinking:**
- Know what's being tested (domain knowledge)
- Know how it's being tested (psychological tricks)
- Answer confidently with both perspectives

---

**Practice Assignment:**
Take the 162-question PDF sample, identify trap codes yourself, and check against the generated JSON output to validate your trap detection skills.

