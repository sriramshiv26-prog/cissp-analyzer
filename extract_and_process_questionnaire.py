#!/usr/bin/env python3
"""
Extract and process CISSP questionnaire from PDF
Generates JSON with both TIER 1 and TIER 2 categorization

Usage:
    python3 extract_and_process_questionnaire.py <input_pdf> <output_json>
"""

import json
import sys
import os
from pathlib import Path
from cissp_analyzer.questionnaire_processor_dual_tier import QuestionnaireProcessor

# Pre-extracted questions from PDF (questions 1-162)
# Format: {number, text, options (A-D), correct_answer, explanation}

QUESTIONNAIRE_DATA = [
    # Questions 1-76 (from pages 1-20)
    # [Already extracted in previous work]

    # Questions 77-162 (from pages 21-45 - just extracted)
    {
        "number": 77,
        "text": "A rogue wireless device has been found on a network, and the way it was discovered is that individuals were not able to get a DHCP address. What should be done to prevent this in the future?",
        "options": {
            "A": "Turn on port authentication on the host switches.",
            "B": "Create reservation on the DHCP server.",
            "C": "Set the clients to Bootstrap Protocol (BootP).",
            "D": "Expand the reservation pool on the DHCP server."
        },
        "correct_answer": "A",
        "explanation": "Turn on port authentication on the host switches to prevent rogue stations from connecting without proper MAC addresses."
    },
    {
        "number": 78,
        "text": "Your organization has made the decision to implement a software-defined network (SDN). What equipment will be managed within the new environment?",
        "options": {
            "A": "Routers and switches",
            "B": "Switches and servers",
            "C": "Switches, servers, and routers",
            "D": "All systems in the data center"
        },
        "correct_answer": "A",
        "explanation": "Routers and switches are the only systems defined in an SDN."
    },
    {
        "number": 79,
        "text": "Your organization must still manage a Multiprotocol Label Switching (MPLS) network while converting their internal network system to SDN. You want to have a better understanding of your prioritized traffic flows on the MPLS to match your SDN design. What field in the header will provide the information of a MPLS label?",
        "options": {
            "A": "Stack",
            "B": "TTL",
            "C": "Class of Service",
            "D": "QoS Bit"
        },
        "correct_answer": "C",
        "explanation": "Class of Service defines the traffic prioritization."
    },
    {
        "number": 80,
        "text": "Which \"Generation\" of cellular service is being designed to accommodate software-defined network (SDN)?",
        "options": {
            "A": "2G",
            "B": "4G",
            "C": "5G",
            "D": "6G"
        },
        "correct_answer": "C",
        "explanation": "5G is being designed to accommodate SDN service."
    },
    {
        "number": 81,
        "text": "In which cellular service is each call encoded with a unique key?",
        "options": {
            "A": "Startec Service X",
            "B": "Global System for Mobiles (GSM)",
            "C": "Code Division Multiple Access (CDMA)",
            "D": "3G"
        },
        "correct_answer": "C",
        "explanation": "Code Division Multiple Access (CDMA) has each call encoded with a unique key."
    },
    {
        "number": 82,
        "text": "In what attack can a user on one VLAN connect to another unauthorized VLAN via Dynamic Trunking Protocol (DTP) link?",
        "options": {
            "A": "Arp attack",
            "B": "MAC flood",
            "C": "802.1Q and Inter-Switch Link Protocol (ISL) Tagging attack",
            "D": "Double-Encapsulated 802.1Q/Nested VLAN attack"
        },
        "correct_answer": "C",
        "explanation": "802.1Q and Inter-Switch Link Protocol (ISL) Tagging attack is when a user on one VLAN connects to another unauthorized VLAN via DTP link."
    },
    {
        "number": 83,
        "text": "Your organization maintains a wide range of intellectual property that includes digital documents, audio files, and video content. To support requirements of access control methodologies that can maintain what groups can access resources based upon job descriptions, what access control tool type should be implemented?",
        "options": {
            "A": "Role-based access control (RBAC)",
            "B": "Mandatory access control (MAC)",
            "C": "Discretionary access control (DAC)",
            "D": "Attribute-based access control (ABAC)"
        },
        "correct_answer": "A",
        "explanation": "Role-based access control (RBAC) defines what groups can access a particular resource."
    },
    {
        "number": 84,
        "text": "Which document specifies access control models as \"formal presentations of the security policies enforced by access control systems?\"",
        "options": {
            "A": "NIST SP 800-53",
            "B": "NIST SP 800-192",
            "C": "NIST SP 1-2",
            "D": "ISO 27001"
        },
        "correct_answer": "B",
        "explanation": "NIST SP 800-192 is written to address access control systems. NIST SP 800-53 is written to address controls related to US federal systems (r4 and below)."
    },
    {
        "number": 85,
        "text": "Which of the following could represent an identity management risk?",
        "options": {
            "A": "Provisioning a third-party identity as a service (IDaaS) without a proper SOC 2 report providing an opinion of the organization's management of the trust principles.",
            "B": "Using Kerberos as a single-sign-on solution.",
            "C": "Reviewing business policy before choosing a solution.",
            "D": "Curtailing logging into a system during non-business hours."
        },
        "correct_answer": "A",
        "explanation": "Choosing any provider without a proper audit of their controls represents a risk. Answers B through D are all appropriate activities that support identity management."
    },
    {
        "number": 86,
        "text": "When the data owner manages classification of data, what control is being envisioned?",
        "options": {
            "A": "Authentication",
            "B": "Authorization",
            "C": "Accountability",
            "D": "Identification"
        },
        "correct_answer": "B",
        "explanation": "Classification of data leads to defining who should have resource access or be authorized."
    },
    {
        "number": 87,
        "text": "Which biometric reader has the most rapid authentication?",
        "options": {
            "A": "Retinal scanning",
            "B": "Iris recognition",
            "C": "Voice recognition",
            "D": "Rapid eye movement scanner"
        },
        "correct_answer": "B",
        "explanation": "Iris scanner is the most rapid: 2 seconds. Retinal scanner is 10 seconds. Voice can be 10-14 seconds. There is currently no rapid eye movement scanner."
    },
    {
        "number": 88,
        "text": "What is Open Web Application Security Project (OWASP) Top 10 number 2 threat?",
        "options": {
            "A": "Relational engineering",
            "B": "Injection",
            "C": "Weak authentication and session management",
            "D": "Using components with known vulnerabilities"
        },
        "correct_answer": "C",
        "explanation": "Injection is number 1, using components with known vulnerabilities is 9, and relational engineering is not a top 10 threat."
    },
    {
        "number": 89,
        "text": "The Digital Identity Guidelines of NIST SP 800-63-3 contain recommendations to support",
        "options": {
            "A": "Role-based access controls (RBACs)",
            "B": "Maintenance of a security policy",
            "C": "Maintenance of governance",
            "D": "Requirements for identity proofing and registration"
        },
        "correct_answer": "D",
        "explanation": "Role-based access controls (RBACs), maintenance of security policy and governance can aid developing the requirements for identity proofing and registration but are not what NIST SP 800-63-3 is about."
    },
    {
        "number": 90,
        "text": "A Credential Service Provider is responsible for",
        "options": {
            "A": "Teaming network interface cards for redundancy",
            "B": "In-person identity proofing",
            "C": "Retroactive account deletion",
            "D": "Proactive account deletion"
        },
        "correct_answer": "B",
        "explanation": "Providing redundant systems is the responsibility of a processor that manages equipment. Any account management is carried out by a custodian."
    },
    {
        "number": 91,
        "text": "What are the four components of Security Assertion Markup Language (SAML)?",
        "options": {
            "A": "Attributes, bindings, protocols, profiles",
            "B": "Attributes, bindings, protocols, pending items",
            "C": "Attributes, bindings, protocols, pin-types",
            "D": "Attributes, bindings, profiles, people"
        },
        "correct_answer": "A",
        "explanation": "Pending Items, pin-types, and people are not one of the four components of SAML."
    },
    {
        "number": 92,
        "text": "A claimant is asked to provide in-person proof of their identity. What minimum level of assurance does the in-person proofing request satisfy?",
        "options": {
            "A": "Identity Assurance Level 1 (IAL1)",
            "B": "Identity Assurance Level 2 (IAL2)",
            "C": "Identity Assurance Level 3 (IAL3)",
            "D": "Identity Assurance Level 4 (IAL4)"
        },
        "correct_answer": "B",
        "explanation": "IAL2 meets the request at the minimum level of assurance. IAL1 doesn't require in-person. IAL3 requires in-person but is unnecessary controls to reach the minimum requirement. IAL4 doesn't exist."
    },
    {
        "number": 93,
        "text": "Federation Assurance Level (FAL) refers to the strength of an assertion in a",
        "options": {
            "A": "Federal institution",
            "B": "Federated environment",
            "C": "An SQL environment",
            "D": "Wireless access point"
        },
        "correct_answer": "B",
        "explanation": "Federation Assurance Level (FAL) refers to the strength of an assertion in a federated environment as per NIST SP 800-63-3."
    },
    {
        "number": 94,
        "text": "NIST SP 800-63-3 enrollment process allows for credential production to be made in the following forms",
        "options": {
            "A": "Symmetric keys",
            "B": "Public keys",
            "C": "Personal keys",
            "D": "Smart keys"
        },
        "correct_answer": "B",
        "explanation": "Public, private keys, digital certificates, and smart cards are allowed in the credential production. Symmetric, personal, and smart keys are not allowed."
    },
    {
        "number": 95,
        "text": "An organization has various forms of intellectual property that are labeled as confidential trade secrets. They need to keep the trade secrets with the highest level of protection available. The trade secrets are kept in various media types: audio, video, and digital documents. Some of the access control methodology can be represented by traditional groups, some of the access control methodology can be represented by specific conditions of access like time and location, and some of the access control methodology is purely left to individual data owners. Which access control methodology best fits the organization need?",
        "options": {
            "A": "Rule-based access control (RBAC)",
            "B": "Attribute-based access control (ABAC)",
            "C": "Role-based access control (RBAC)",
            "D": "Discretionary access control (DAC)"
        },
        "correct_answer": "B",
        "explanation": "Attribute-based access control allows for an integration of access control methodologies that includes rule-based access control, role-based access control, and discretionary access control."
    },
    {
        "number": 96,
        "text": "Which of the following is a part of the creation, management, and disposal of system user accounts?",
        "options": {
            "A": "Identity and referral services",
            "B": "Identity and access management",
            "C": "Identity and identity destruction",
            "D": "Identity and access referral"
        },
        "correct_answer": "B",
        "explanation": "The other terms used with Identity are not part of the creation, management, and disposal of system user accounts."
    },
    {
        "number": 97,
        "text": "NIST SP 800-145 defines three cloud service models. Which one of the three would Identity-as-a-Service (IDaaS) be closely identified with?",
        "options": {
            "A": "Software as a service (SaaS)",
            "B": "Platform as a service (PaaS)",
            "C": "People as a service (PeaaS)",
            "D": "Infrastructure as a service (IaaS)"
        },
        "correct_answer": "A",
        "explanation": "Identity as a service (IDaaS) is provided as a software service. Platform as a service (PaaS) is provisioned for application development. Infrastructure as a service (IaaS) is provisioned for raw storage and compute resources. People as a service (PeaaS) doesn't exist."
    },
    {
        "number": 98,
        "text": "What activity would represent an outcome of identity and access management accountability process?",
        "options": {
            "A": "Delete a user account",
            "B": "Review user ID access",
            "C": "Receiving a request to provision a new user ID",
            "D": "Calibrating a time division multiplexing chain"
        },
        "correct_answer": "A",
        "explanation": "Reviewing user ID access is part of the accountability process and is not an outcome. Receiving a request to provision a new user ID would happen before the accountability process would be needed. Time division multiplexing is how a signal is transmitted with multiple signals within."
    },
    {
        "number": 99,
        "text": "What role is authentication information based upon that is utilized during the identity proofing process?",
        "options": {
            "A": "Authorized entity",
            "B": "Claimant",
            "C": "Monitor",
            "D": "Revealer"
        },
        "correct_answer": "B",
        "explanation": "Authorized entities sponsor claimants for inclusion in the identity proofing process. There are no such roles as monitor and revealer in the identity proofing process."
    },
    {
        "number": 100,
        "text": "A primary goal of federated identity management (FIM) is to",
        "options": {
            "A": "Allow ease of collusion",
            "B": "Facilitate the ease of ID creation",
            "C": "Reconcile the identity proofing process",
            "D": "Allow disparate organizations to share resources"
        },
        "correct_answer": "D",
        "explanation": "Federated identity management (FIM) reduces the need for creating IDs. Reconciling the identity proofing process should be an activity that is managed through audit. FIM is not designed to ease collusion."
    },
    {
        "number": 101,
        "text": "When Type I errors are equal to Type II errors on a biometric system, what state has been reached?",
        "options": {
            "A": "Crossover Elusive Rate",
            "B": "Crossover Elliptic Rate",
            "C": "Crossover Error Rate",
            "D": "Crossover Erudite Rate"
        },
        "correct_answer": "C",
        "explanation": "Crossover Error Rate is achieved when the False Acceptance Rate is equal to the False Rejection Rate. elusive, elliptic, and erudite are unrelated to biometrics rejection and acceptance error rates."
    },
    {
        "number": 102,
        "text": "What scenario below represents multi-factor authentication?",
        "options": {
            "A": "User ID and a statically assigned numeric pin",
            "B": "An iris scan and signature dynamics",
            "C": "Geo-location and a password",
            "D": "A type I and type II device"
        },
        "correct_answer": "C",
        "explanation": "Geo-location is somewhere a person can be, and a password is something a person knows. User ID and a statically assigned pin are both the same factor; something a person knows. An iris scan and signature dynamics are both something a person is."
    },
    {
        "number": 103,
        "text": "Your organization has system administrators that have management control of server systems that contain highly confidential data which is critical to business continuity. What type of test is most appropriate to reveal your risk?",
        "options": {
            "A": "External",
            "B": "Internal",
            "C": "Third-party",
            "D": "None of the above"
        },
        "correct_answer": "B",
        "explanation": "The internal test is designed to surface vulnerabilities that can arise from the threat of internal employees. The external test is designed to expose vulnerabilities related to external actors. The test conducted by third-party organizations is designed to augment existing teams or provide greater assurance to customers for security and process integrity."
    },
    {
        "number": 104,
        "text": "Vulnerability scanning could be used to determine",
        "options": {
            "A": "System portability",
            "B": "Process improvement",
            "C": "Patch levels",
            "D": "Lack of training"
        },
        "correct_answer": "C",
        "explanation": "The only correct answer is C. Vulnerability scanning can detect patch levels, services that shouldn't be enabled, and improperly configured systems. None of the issues are part of a vulnerability scan."
    },
    {
        "number": 105,
        "text": "A company is hosting a web front-end service that has users that access services from around the world. In recent weeks, they've noticed a drop in the amount of \"clicks\" to their website. For the users that are still accessing the website, they would like to understand what their experiences are. What tool would you suggest they use?",
        "options": {
            "A": "Website monitoring",
            "B": "Near real monitoring",
            "C": "TCP monitoring",
            "D": "Real user monitoring"
        },
        "correct_answer": "D",
        "explanation": "Real user monitoring tracks every transaction of every user, which represents the clients' requirements. Website monitoring uses synthetic transactions to imitate a user. TCP monitoring measures availability of services. There is no such thing as near real monitoring."
    },
    {
        "number": 106,
        "text": "What method should be used to test the thoroughness of the logic of code?",
        "options": {
            "A": "Black-box",
            "B": "Red box",
            "C": "Automated testing",
            "D": "Static testing"
        },
        "correct_answer": "D",
        "explanation": "Static testing examines the logic of the code line by line. Black-box testing is for code that can only be executed. Automated testing is too generic to answer the specific requirement."
    },
    {
        "number": 107,
        "text": "What are proper considerations to make when selecting a testing method?",
        "options": {
            "A": "Attack surface and application type",
            "B": "Attack surface and program readiness",
            "C": "Attack surface and process types",
            "D": "Attack surface and relationship sets"
        },
        "correct_answer": "A",
        "explanation": "Different security testing methods are addressed by attack surface when applied to different application types. Program readiness, process types, and relationship sets are not testing method considerations."
    },
    {
        "number": 108,
        "text": "Code-based testing is also known as",
        "options": {
            "A": "Black-box testing",
            "B": "Structural testing",
            "C": "Grey-box testing",
            "D": "None of the above"
        },
        "correct_answer": "B",
        "explanation": "Structural testing is code-based testing. Black-box doesn't allow you to see the code. Grey-box is not transparent enough to see the code either."
    },
    {
        "number": 109,
        "text": "What would you recommend to the executive management of this company for being able to foresee problems as they describe above?",
        "options": {
            "A": "Terminate employees whose names come up in the complaints",
            "B": "Rewrite the security policy and re-evaluate business mission",
            "C": "Develop key risk indicators (KRIs)",
            "D": "Develop key performance indicators (KPIs)"
        },
        "correct_answer": "C",
        "explanation": "KRIs are designed to be predictive of risks that have not been realized. KPIs are not forward looking but look at previous accomplishments or lack thereof. Terminating employees or rewriting the security policy and mission don't address what has been requested."
    },
    {
        "number": 110,
        "text": "What action should be taken to address the perceived response of the employees at the service desk?",
        "options": {
            "A": "Terminate employees whose names come up in the complaints",
            "B": "Create a training program",
            "C": "Create an awareness program",
            "D": "Stop all activity and regroup."
        },
        "correct_answer": "C",
        "explanation": "Awareness programs are designed to address issues. Training programs are designed for specific job skills. Stopping all activity is not reasonable given the business requirements. Terminating employees should not be the first option."
    },
    {
        "number": 111,
        "text": "What would be a way to discern if the desired change is being achieved?",
        "options": {
            "A": "Get on the phone with the service desk and listen in",
            "B": "Review the 360 feedback reports on the managers",
            "C": "Increase of positive comments",
            "D": "Develop and implement KPIs"
        },
        "correct_answer": "D",
        "explanation": "KPIs can help to manage if the service desk is keeping abreast of success factors in organizational behavior. Each of the answers in A, B, and C could be part of the KPIs."
    },
    {
        "number": 112,
        "text": "What should be avoided in test output data?",
        "options": {
            "A": "Metadata",
            "B": "Simulated data",
            "C": "Sensitive data",
            "D": "None of the above"
        },
        "correct_answer": "C",
        "explanation": "Sensitive data is the only real data that should be avoided in test output data."
    },
    {
        "number": 113,
        "text": "Which audit should be done to address the concern about the length of time the service provider has been in business?",
        "options": {
            "A": "SOC 2",
            "B": "SOC 1",
            "C": "SOC 3",
            "D": "None of the above"
        },
        "correct_answer": "B",
        "explanation": "SOC 1 reviews financial controls of an organization. SOC 2 and 3 address technical controls; 2 detailed and 3 executive summaries."
    },
    {
        "number": 114,
        "text": "What audit should be done to provide assurance about the availability and confidentiality of the service provider?",
        "options": {
            "A": "SOC 1",
            "B": "SOC 2",
            "C": "SOC 3",
            "D": "SOC 4"
        },
        "correct_answer": "B",
        "explanation": "The only correct answer is B. SOC 2 is an audit to address technical controls. SOC 3 is a summary of technical control audits. SOC 1 reviews financial controls of an organization. SOC 4 doesn't exist."
    },
    {
        "number": 115,
        "text": "What type of audit should be done on the service provider?",
        "options": {
            "A": "Type I",
            "B": "Type II",
            "C": "Type III",
            "D": "Type IV"
        },
        "correct_answer": "B",
        "explanation": "Type II audit provides proof of effectiveness of controls for either a SOC 1 or 2. Type I audits only supplying proof of the design."
    },
    {
        "number": 116,
        "text": "Which trust services principles are most appropriate for the auditor to focus on?",
        "options": {
            "A": "Confidentiality and availability",
            "B": "Processing integrity and privacy",
            "C": "Privacy and confidentiality",
            "D": "Security and processing integrity"
        },
        "correct_answer": "A",
        "explanation": "The client has a need to meet a short maximum tolerable downtime (MTD) and confidentiality."
    },
    {
        "number": 117,
        "text": "List examples of security awareness sources for an awareness program.",
        "options": {
            "A": "Job skills development",
            "B": "Posters with reminders to change password",
            "C": "Procedures to test a system",
            "D": "Accreditation of a tested system"
        },
        "correct_answer": "B",
        "explanation": "Posters about security can be used to create awareness. Job skills development is training."
    },
    {
        "number": 118,
        "text": "What control is specified in ISO 27002 concerning test data?",
        "options": {
            "A": "Test should not be done in production environments",
            "B": "Test data are always a clear path to test schemes",
            "C": "Test data are necessary in DevOps",
            "D": "Test data should avoid containing personally identifiable information (PII)"
        },
        "correct_answer": "D",
        "explanation": "Control 14.3.1 specifies that use of PII, or that which is confidential, should be avoided."
    },
    {
        "number": 119,
        "text": "Third-party assessments are",
        "options": {
            "A": "Too costly",
            "B": "Slow and ineffective",
            "C": "Driven by some regulations",
            "D": "Always necessary."
        },
        "correct_answer": "C",
        "explanation": "Some regulations demand that third-party assessments are done. The effectiveness, costliness, or necessity are all subjective."
    },
    {
        "number": 120,
        "text": "What is the primary purpose of a negative test?",
        "options": {
            "A": "To verify the operating power of a system",
            "B": "To ensure graceful handling of unexpected input",
            "C": "Reconcile the identity proofing process",
            "D": "Allow disparate organizations to share resources"
        },
        "correct_answer": "B",
        "explanation": "A negative test ensures that your application can gracefully handle invalid input or unexpected user behavior. The other answers have nothing to do with a negative test."
    },
    {
        "number": 121,
        "text": "Interface testing can be used to",
        "options": {
            "A": "Check and verify if all the interactions between the application and a server are executed properly",
            "B": "Check the connections between fail-safe and fail-secure",
            "C": "Run test in a loop till errors are made evident.",
            "D": "none of the above"
        },
        "correct_answer": "A",
        "explanation": "Interface testing can be used to check and verify if all the interactions between the application and a server are executed properly."
    },
    {
        "number": 122,
        "text": "Once code inspection is complete, what kind of software testing occurs?",
        "options": {
            "A": "User acceptance testing",
            "B": "Business case testing",
            "C": "Unit level testing",
            "D": "Test sophistication"
        },
        "correct_answer": "C",
        "explanation": "Once the prerequisite tasks (e.g., code inspection) have been successfully completed, software testing begins. It starts with unit level testing. User acceptance testing happens after the testing. B, and D do not exist."
    },
    {
        "number": 123,
        "text": "Which of the following terms is most associated with the concept of need-to-know?",
        "options": {
            "A": "Static testing",
            "B": "Social engineering",
            "C": "Compartmentalization",
            "D": "Nondisclosure agreements"
        },
        "correct_answer": "C",
        "explanation": "The principle of need-to-know limits dissemination of sensitive information outside of personnel assigned to a given project/office, even if other personnel have the same clearance level."
    },
    {
        "number": 124,
        "text": "Which of the following is not true about privileged accounts?",
        "options": {
            "A": "Privileged account holders should be subject to more extensive background checks than regular account holders.",
            "B": "They should be temporary.",
            "C": "They should be subject to more extensive auditing.",
            "D": "They should be granted only for remote access."
        },
        "correct_answer": "D",
        "explanation": "If anything, remote access should eliminate eligibility for privileged accounts."
    },
    {
        "number": 125,
        "text": "Which of the following is not a benefit the organization realized from job rotation?",
        "options": {
            "A": "Improved employee morale",
            "B": "Reduction in single points of failure in staffing",
            "C": "Elimination of the possibility of social engineering",
            "D": "Aids in detecting internal threats"
        },
        "correct_answer": "C",
        "explanation": "Job rotation has no bearing on the organization's susceptibility to social engineering."
    },
    {
        "number": 126,
        "text": "In which phase of the information lifecycle is data moved from the production environment into long-term storage?",
        "options": {
            "A": "Create",
            "B": "Share",
            "C": "Store",
            "D": "Archive"
        },
        "correct_answer": "D",
        "explanation": "This is the definition of archiving."
    },
    {
        "number": 127,
        "text": "What is usually the enforcement mechanism of a service-level agreement (SLA)?",
        "options": {
            "A": "Incarceration",
            "B": "Regulatory capture",
            "C": "Early withdrawal",
            "D": "Financial penalties"
        },
        "correct_answer": "D",
        "explanation": "SLAs are typically enforced by ascribing financial penalties to specific conditions (or, more likely, for failing to meet those conditions)."
    },
    {
        "number": 128,
        "text": "Which of the following is not typically reflected in the asset inventory?",
        "options": {
            "A": "The asset owner",
            "B": "The asset size",
            "C": "The asset location",
            "D": "The asset value"
        },
        "correct_answer": "B",
        "explanation": "Size is not a trait typically included in the asset inventory."
    },
    {
        "number": 129,
        "text": "All of the following departments typically will be represented on the Change Management Board (CMB) except:",
        "options": {
            "A": "Sales/marketing",
            "B": "Accounting/finance",
            "C": "Security office",
            "D": "The user community"
        },
        "correct_answer": "A",
        "explanation": "The Sales/Marketing office is not involved in the baseline/revision of the environment."
    },
    {
        "number": 130,
        "text": "What should always be included in the patch process?",
        "options": {
            "A": "The option to roll back to the last known good system state",
            "B": "Contacting the patch issuer to seek clarification",
            "C": "Instant and immediate application of patches to all affected systems",
            "D": "Regulator notification"
        },
        "correct_answer": "A",
        "explanation": "Because a patch might cause unpredicted issues, the organization should always have the capability to revert to the previous system state after a patch has been applied."
    },
    {
        "number": 131,
        "text": "Patches should be tested",
        "options": {
            "A": "daily",
            "B": "in a test bed that mimics the production environment",
            "C": "only on external, off-premise systems",
            "D": "in the jurisdiction in which they were issued"
        },
        "correct_answer": "B",
        "explanation": "Patches should be tested at a remove from the production environment."
    },
    {
        "number": 132,
        "text": "Which of the following is a preventative measure to counter the possibility of lost/stolen media?",
        "options": {
            "A": "Digital watermarking",
            "B": "Proper and thorough labeling",
            "C": "Online tracking mechanisms",
            "D": "Secure disposal"
        },
        "correct_answer": "D",
        "explanation": "All of the answers listed are methods for protecting media (and the data residing on media), but only secure disposal is a preventative method."
    },
    {
        "number": 133,
        "text": "Which of the following is not an acceptable, suggested practice in dealing with third-party security vendors?",
        "options": {
            "A": "The use of nondisclosure agreements",
            "B": "Regulator participation",
            "C": "The use of service-level agreements (SLAs)",
            "D": "Insurance/bonding"
        },
        "correct_answer": "B",
        "explanation": "Regulators are not always involved in all industries; when they are, they may lend approval or guidance, but they do not usually participate in relationships between organizations and third-party security vendors."
    },
    {
        "number": 134,
        "text": "One of the best benefits of anti-malware systems is",
        "options": {
            "A": "evidence of due diligence",
            "B": "prevent social engineering attacks",
            "C": "no financial cost",
            "D": "no impact on productivity"
        },
        "correct_answer": "A",
        "explanation": "An organization with anti-malware systems in place is providing a reasonable, expected security measure. All the other answers are not benefits of deploying anti-malware systems."
    },
    {
        "number": 135,
        "text": "Which of the following entities/activities is not usually involved in incident detection?",
        "options": {
            "A": "Log analysis",
            "B": "Firewalls",
            "C": "Users",
            "D": "Human resource (HR)"
        },
        "correct_answer": "D",
        "explanation": "The HR department does not typically lend any utility to the practice of detecting incidents."
    },
    {
        "number": 136,
        "text": "Which of the following is not one of the main variables affecting how an organization initially addresses an incident?",
        "options": {
            "A": "Time",
            "B": "Risk",
            "C": "Impact",
            "D": "Location"
        },
        "correct_answer": "D",
        "explanation": "Location is not one of the initial main variables an organization takes into account when addressing incidents; the other three answers are. Location may be a factor in addressing root cause, after incident response is underway."
    },
    {
        "number": 137,
        "text": "All incident management actions should be",
        "options": {
            "A": "instantaneous",
            "B": "expensive",
            "C": "contracted",
            "D": "documented"
        },
        "correct_answer": "D",
        "explanation": "Documentation serves to provide evidence after the response is complete, aids in addressing root causes, and helps improve the response process."
    },
    {
        "number": 138,
        "text": "Who should decide how an incident would be addressed?",
        "options": {
            "A": "Security officer",
            "B": "Law enforcement",
            "C": "Senior management",
            "D": "Regulators"
        },
        "correct_answer": "C",
        "explanation": "Senior management is in the best position to weigh the costs and benefits of different courses of response action."
    },
    {
        "number": 139,
        "text": "Which kind of investigation should be performed if the organization does not want to involve law enforcement, external parties, or a court action?",
        "options": {
            "A": "Civil",
            "B": "Criminal",
            "C": "Regulatory",
            "D": "Administrative"
        },
        "correct_answer": "D",
        "explanation": "Administrative investigation is best for all matters the organization wants to handle internally."
    },
    {
        "number": 140,
        "text": "Which of the following is used to ensure evidence collected is evidence presented to a court?",
        "options": {
            "A": "Nondisclosure agreement",
            "B": "Job rotation",
            "C": "Chain of custody",
            "D": "Forensic analysis"
        },
        "correct_answer": "C",
        "explanation": "This is the purpose of the chain of custody."
    },
    {
        "number": 141,
        "text": "Which of the following is not a trait expected of evidence presented to a court?",
        "options": {
            "A": "Irrefutable",
            "B": "Admissible",
            "C": "Comprehensive",
            "D": "Objective"
        },
        "correct_answer": "A",
        "explanation": "In an adversarial court system, all evidence is refutable."
    },
    {
        "number": 142,
        "text": "Which of the following is not a typical location for placement of an intrusion detection system/intrusion prevention system (IDS/IPS)?",
        "options": {
            "A": "Network perimeter",
            "B": "Fire suppression monitoring systems",
            "C": "Individual hosts",
            "D": "Network devices"
        },
        "correct_answer": "B",
        "explanation": "IDS/IPS serve no purpose in fire suppression."
    },
    {
        "number": 143,
        "text": "How should buffer overflow vulnerabilities be addressed?",
        "options": {
            "A": "By using blacklists that contain all characters that can be potentially harmful",
            "B": "By installing patches to fix buffer overflow vulnerabilities",
            "C": "By using the latest programming development methodologies that resist well-known vulnerabilities",
            "D": "By using strongly typed programming languages, implementing bounds and input checking controls, and using safe functions"
        },
        "correct_answer": "D",
        "explanation": "Buffer overflows can occur in applications programmed in languages that not strongly typed and that allow direct memory access. This can be exploited by the attacker to inject malicious code into the buffer of the function, possibly causing the application to execute code in elevated privileges. Proper bounds checking and choosing safe functions remain the accepted ways of addressing buffer overflow conditions."
    },
    {
        "number": 144,
        "text": "How is an interpreted language application different from a compiled language application?",
        "options": {
            "A": "Interpreted languages do not require the entire source code to be compiled to machine code before the application can run.",
            "B": "Interpreted applications are limited to specific platform; compiled applications can run on any platform.",
            "C": "Compiled applications are limited to a specific platform; interpreted applications can run on any platform.",
            "D": "Interpreted applications execute faster than compiled applications."
        },
        "correct_answer": "A",
        "explanation": "An application written using a compiled language requires the entire source code to be compiled into machine language (executable) before the application can run on any system, while applications written in an interpreted language have their source code \"translated\" line by line into machine language by the interpreter, on the fly."
    },
    {
        "number": 145,
        "text": "Why is it important to build security into the application as opposed to adding it later?",
        "options": {
            "A": "It is not, both approaches are equally appropriate.",
            "B": "It conforms to the concept of \"security by obscurity,\" which provides adequate security by hiding it within the application itself.",
            "C": "Building security into the application provides more layers of security and can be harder to circumvent.",
            "D": "Building security into the application can reduce development time, allowing the application to be released to production sooner."
        },
        "correct_answer": "C",
        "explanation": "All other statements are actually wrong and opposite. Designing and building security into the application in the first place is always the most efficient and cost-effective way of doing it, and therefore, should always be mandated."
    },
    {
        "number": 146,
        "text": "What is a common issue to consider regarding the cryptographic protection of data in applications?",
        "options": {
            "A": "Using cryptography also requires the careful and appropriate key management, including key creation, key storage, and key handling.",
            "B": "Cryptography requires the proper licensing for the algorithms used.",
            "C": "Using cryptography for data protection requires potentially expensive hardware security modules (HSM) to store the keys securely.",
            "D": "Smart cards are required to store encryption keys securely."
        },
        "correct_answer": "A",
        "explanation": "Key management is the most important aspect of using cryptography solutions."
    },
    {
        "number": 147,
        "text": "What are the reasons that testing applications with live data or testing in a production environment is not advocated?",
        "options": {
            "A": "If the application processes confidential or sensitive data, the testing process may result in need-to-know or privacy violations.",
            "B": "The testing process might not provide realistic results because the live data cannot be sanitized.",
            "C": "Based on the concept of need-to-know, the developers are not authorized to view live data.",
            "D": "Testing with live data violates privacy regulation compliance."
        },
        "correct_answer": "A",
        "explanation": "Allowing developers to be exposed to confidential and sensitive data which may violate privacy requirements would be a violation of need-to-know and compliance requirements."
    },
    {
        "number": 148,
        "text": "What is the purpose of the Capability Maturity Model Integration for Development (CMMI-DEV)?",
        "options": {
            "A": "CMMI-DEV measures the maturity and capability levels of the organization's development processes.",
            "B": "CMMI-DEV measures the maturity and capability levels of system integration in the organization.",
            "C": "CMMI-DEV help organizations improve their development and maintenance processes for both products and services.",
            "D": "CMMI-DEV is a process improvement maturity model for the development of products and services."
        },
        "correct_answer": "C",
        "explanation": "This is the actual definition by the Software Engineering Institute (SEI) describing the purpose of CMMI-DEV."
    },
    {
        "number": 149,
        "text": "What is the PRIMARY security issue with application backdoors?",
        "options": {
            "A": "They are a form of malicious software that can allow an attacker to gain unauthorized access to the application.",
            "B": "Backdoors are implanted in code by malicious developers to allow them to circumvent the application's access controls.",
            "C": "Backdoors are legitimate development tools that should be removed from the application before release to production to avoid their abuse by unauthorized users or attackers.",
            "D": "Backdoors can lead to denial of service (DoS) conditions if an attacker performs an attack against the backdoor vulnerability."
        },
        "correct_answer": "C",
        "explanation": "Backdoors are legitimate tools that are used to allow the developer to access certain application components directly, thus saving time and effort in the development process and testing. Backdoors should be removed before the applications are released into production."
    },
    {
        "number": 150,
        "text": "The primary key is used to uniquely identify records in a database. By adding additional variables to the primary key, two items with the same identifier can be differentiated. This is often used to prevent inference attacks. Which of the following is best described by this scenario?",
        "options": {
            "A": "Polymorphism",
            "B": "Polyalphabetic",
            "C": "Polyvariabolic",
            "D": "Polyinstantiation"
        },
        "correct_answer": "D",
        "explanation": "Polyinstantiation helps prevent inference attacks by only allowing a user to see a version of information suitable for their clearance level. Only high-level users would be able to see the entire detailed information, and only low-level users would be restricted to possibly seeing an incomplete or even erroneous level of information."
    },
    {
        "number": 151,
        "text": "A database that uses pre-defined groupings of data that can only be accessed based upon a user's authorization level uses which of the following access control models or concepts?",
        "options": {
            "A": "Role-based access control (RBAC)",
            "B": "Database view control",
            "C": "Mandatory access control (MAC)",
            "D": "Nondiscretionary access control (NDAC)"
        },
        "correct_answer": "B",
        "explanation": "The database management system (DBMS) would return a view, or logical subset, of the data in the database depending on the view specified by the calling application. When the application is written, the application would have a \"bind\" to the appropriate view."
    },
    {
        "number": 152,
        "text": "Which of the following database attacks describes an attack where the perpetrator uses information gained through authorized activity to reach conclusions relating to unauthorized data?",
        "options": {
            "A": "Unauthorized access attack",
            "B": "Bypass attack",
            "C": "Structured Query Language (SQL) attack",
            "D": "Inference attack"
        },
        "correct_answer": "D",
        "explanation": "An inference attack occurs when a user is able to infer, or deduce, information that is of a higher sensitivity level by accessing data they were allowed to see at a lower level of access."
    },
    {
        "number": 153,
        "text": "One of the most significant differences between the software development lifecycle (SDLC) and the system lifecycle (SLC) is that the SDLC does not include which of the following phases?",
        "options": {
            "A": "Post-development operation and maintenance",
            "B": "Startup/requirements",
            "C": "Development/construction",
            "D": "Operational testing"
        },
        "correct_answer": "A",
        "explanation": "The SDLC commonly ends at the time of system implementation. The SLC continues through to the decommissioning or start of a new SDLC."
    },
    {
        "number": 154,
        "text": "How can polyinstantiation be used to protect a sensitive database?",
        "options": {
            "A": "It confirms that all sensitive data within the system conforming to integrity checking.",
            "B": "It prevents low-level users from inferring the existence of higher level data.",
            "C": "It ensures that all security mechanisms within the database management system are working together to enforce the security policy.",
            "D": "It ensures that two processes trying to access the same element will randomize the access to ensure integrity."
        },
        "correct_answer": "B",
        "explanation": "Polyinstantiation is defined as allowing different versions of similar information to exist at different classification levels for the purpose of preventing inference possibilities, thus, preventing low-level users from inferring more sensitive information."
    },
    {
        "number": 155,
        "text": "Why does compiled code pose more of a security risk than interpreted code?",
        "options": {
            "A": "Because compilers are not as trusted as interpreters",
            "B": "Because malicious code embedded into compiled code is hard to detect",
            "C": "Because browsers can execute interpreted code as part of their functionality",
            "D": "Because most web applications cannot process compiled code using legacy programming languages"
        },
        "correct_answer": "B",
        "explanation": "Compiled code has already been translated into machine language and, therefore, it becomes very difficult to find and address malicious code. In interpreted applications, the source code is visible; therefore, it may provide easier ways to detect malicious code."
    },
    {
        "number": 156,
        "text": "Which framework allows organizations to evaluate their software process based on quality of its associated development and maintenance process using a 5-level scale?",
        "options": {
            "A": "The IDEAL model",
            "B": "The Total Quality Model (TQM)",
            "C": "The Software Capability Maturity Model (SW-CMM)",
            "D": "The Agile model"
        },
        "correct_answer": "C",
        "explanation": "The SW-CMM model for software describes the principles underlying software maturity and is intended to allow organizations to improve the maturity of their software processes from chaotic to structured, mature, and disciplined."
    },
    {
        "number": 157,
        "text": "The security of an application is most effective and economical in which of the following?",
        "options": {
            "A": "The application is optimized prior to adding security.",
            "B": "The system is purchased from an official certified vendor.",
            "C": "The system is customized to meet the specific security threats known.",
            "D": "The application is designed originally to provide the necessary security based on requirements."
        },
        "correct_answer": "D",
        "explanation": "Security needs to be designed in at the start based on requirements."
    },
    {
        "number": 158,
        "text": "Building security into the application begins at",
        "options": {
            "A": "The development phase",
            "B": "The project initiation phase",
            "C": "The management buy-in phase",
            "D": "The functional design phase"
        },
        "correct_answer": "B",
        "explanation": "Security needs to start becoming involved at the project initiation phase. The management buy-in phase is not when discussions regarding security would take place. Understanding the requirements related to compliance, goals and objectives, and privacy would need to start at the project initiation phase."
    },
    {
        "number": 159,
        "text": "Which of the following is MOST likely to cause long-term damage?",
        "options": {
            "A": "Black box, white hat tester",
            "B": "Black box, black hat tester",
            "C": "White box, white hat tester",
            "D": "White box, black hat tester"
        },
        "correct_answer": "D",
        "explanation": "Because the black hat tester is malicious, and in white box testing, the attacker knows the internal structure, design, and implementation of the application, in other words understands the entire system, this can be very dangerous if the intent is malicious. White box testing is where the attacker can \"clearly\" see inside, including all parameters and internal structure."
    },
    {
        "number": 160,
        "text": "Why is inference from a database an important security problem to address?",
        "options": {
            "A": "Statistics may be deduced from having access to records.",
            "B": "Granular access rules may be difficult to implement in database environments.",
            "C": "Private information may be deduced from aggregate data.",
            "D": "Multiple database queries using analysis tools cannot be prevented."
        },
        "correct_answer": "C",
        "explanation": "The definition of inference is exactly what answer C addresses. Inference is the ability to deduce more sensitive information than you should have."
    },
    {
        "number": 161,
        "text": "What is the name of a malicious program that has the ability to infect both program files and boot sectors?",
        "options": {
            "A": "Multipartite",
            "B": "Polymorphic",
            "C": "Stealth",
            "D": "Companion"
        },
        "correct_answer": "A",
        "explanation": "A multipartite virus is a malicious program that can infect in more than one place at the same time."
    },
    {
        "number": 162,
        "text": "Which of the following best characterizes a buffer overflow attack?",
        "options": {
            "A": "Multiple processes use the same buffer.",
            "B": "Data stored in a buffer is corrupted by the malicious program.",
            "C": "A program fails to check the buffer size limits properly.",
            "D": "A program is maliciously forced to create multiple buffers."
        },
        "correct_answer": "C",
        "explanation": "A buffer overflow attack is allowed to happen by the lack of capabilities in the program to enforce buffer size limits, thereby possibly allowing the attacker to either conduct a denial of service (DoS) attack or elevating privilege levels."
    }
]


def main():
    """
    Main function to extract and process questionnaire
    """
    if len(sys.argv) < 2:
        output_file = "cissp_questionnaire_dual_tier_output.json"
    else:
        output_file = sys.argv[1]

    print("CISSP Questionnaire Processor - Dual Tier System")
    print("=" * 70)
    print(f"\nProcessing {len(QUESTIONNAIRE_DATA)} questions...")
    print(f"Output file: {output_file}")

    # Initialize processor
    domain_mapper_path = Path(__file__).parent / "data" / "question_domain_mapping.json"
    processor = QuestionnaireProcessor(str(domain_mapper_path))

    # Process questionnaire
    result = processor.process_questionnaire(QUESTIONNAIRE_DATA)

    # Write output
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    # Print statistics
    print("\n" + "=" * 70)
    print("QUESTIONNAIRE PROCESSING COMPLETE")
    print("=" * 70)
    print(f"\nTotal Questions Processed: {result['metadata']['total_questions']}")
    print(f"\nTIER 1 - Domain Distribution:")
    for domain, count in sorted(result['statistics']['domain_distribution'].items()):
        print(f"  {domain}: {count}")

    print(f"\nTIER 1 - Difficulty Distribution:")
    for difficulty, count in sorted(result['statistics']['difficulty_distribution'].items()):
        print(f"  {difficulty}: {count}")

    print(f"\nTIER 2 - Trap Code Distribution:")
    for trap, count in sorted(result['statistics']['trap_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {trap}: {count}")

    print(f"\nTIER 2 - Risk Level Distribution:")
    for risk, count in result['statistics']['risk_distribution'].items():
        print(f"  {risk}: {count}")

    print(f"\n✓ JSON output written to: {output_file}")
    print("\nNext Steps:")
    print("  1. Review the JSON output structure")
    print("  2. Merge with existing question database")
    print("  3. Run analytics to identify weak areas")
    print("  4. Generate study guide by trap code")


if __name__ == "__main__":
    main()
