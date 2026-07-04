# Where to Download Templates & Examples

**Last Updated:** July 4, 2026 | **Version:** 1.0 | **Status:** Live on GitHub

---

## 📥 Download Location

All templates and examples are on GitHub:

**Repository:** https://github.com/sriramshiv26-prog/cissp-analyzer

**Direct Download Link:** https://github.com/sriramshiv26-prog/cissp-analyzer/archive/refs/heads/main.zip

---

## 🎯 What You Can Download

### Category 1: Real Working Examples (Download & Use)

#### 1. EXAMPLE_answer_key.json
**What:** 30 sample CISSP questions with answers (JSON format)  
**Size:** 2.9 KB  
**Use:** See working JSON answer key format  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_answer_key.json
Click: Raw button → Right-click → Save As
Or: Copy content into your text editor
```

**What It Contains:**
```json
{
  "1": {
    "letter": "A",
    "text": "AES uses 128, 192, or 256-bit encryption..."
  },
  "2": {
    "letter": "B",
    "text": "Public key infrastructure enables..."
  },
  ...
  "30": {
    "letter": "B",
    "text": "Sample explanation..."
  }
}
```

#### 2. EXAMPLE_answer_key.csv
**What:** Same 30 questions in CSV format  
**Size:** 1.7 KB  
**Use:** Easy to edit in Excel or any spreadsheet app  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_answer_key.csv
Click: Raw button → Right-click → Save As → Save as .csv
Or: Click Download Raw File icon
```

**What It Contains:**
```
Question,Answer,Explanation
1,A,AES uses 128, 192, or 256-bit encryption...
2,B,Public key infrastructure enables...
...
30,B,Sample explanation...
```

#### 3. EXAMPLE_student_answers.xlsx ⭐ MOST USEFUL
**What:** Real Excel file with 4 students, 20 questions  
**Size:** 14 KB  
**Use:** Download, open in Excel, see exact format needed  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_student_answers.xlsx
Click: Download Raw File (or right-click → Save As)
OR: Click the file → Download button on GitHub
```

**What It Contains:**
- Sheet 1: Student Answers
  - Column A: Question (Q1, Q2, Q3, ... Q20)
  - Column B: Alice's answers (A, B, C, 1-A,2-B,3-C,4-D, etc.)
  - Column C: Bob's answers
  - Column D: Carol's answers
  - Column E: David's answers
  
- Sheet 2: Instructions
  - How to format each answer type
  - Examples of correct formats
  - What NOT to do

---

### Category 2: Template Files (Copy & Customize)

#### 4. TEMPLATE_answer_key.json
**What:** Blank JSON structure (no example data)  
**Size:** 1.5 KB  
**Use:** Copy and create your own answer key  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/TEMPLATE_answer_key.json
Click: Raw → Right-click → Save As
Edit in: Text editor, VSCode, or online JSON editor
```

**How to Use:**
1. Download file
2. Open in text editor
3. Replace the sample structure with your 125 questions
4. Save as `exam_1_answer_key.json`

#### 5. TEMPLATE_student_answers.md
**What:** Guide to Excel format (not a file to download as template)  
**Size:** 7.7 KB  
**Use:** Reference guide for creating Excel files  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/TEMPLATE_student_answers.md
View: Click to read on GitHub (no download needed)
OR: Right-click → Save As to save locally
```

**Contains:**
- Excel wide format (recommended)
- Excel tall format (alternative)
- All 6 answer format variations
- Multi-part answer examples
- Common mistakes & fixes

#### 6. TEMPLATE_directory_structure.md
**What:** Guide to folder organization  
**Size:** 12 KB  
**Use:** Understand how to organize your project  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/TEMPLATE_directory_structure.md
View: Click to read on GitHub (no download needed)
OR: Right-click → Save As
```

---

### Category 3: Documentation (Read Online or Download)

#### 7. QUICK_SETUP_CARD.txt ⭐ START HERE
**What:** 7-step quick start guide (printable)  
**Size:** ~10 KB  
**Download & Print:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/QUICK_SETUP_CARD.txt
Click: Raw → Print (Ctrl+P / ⌘P)
OR: Right-click → Save As → Open in text editor → Print
```

#### 8. FORMATS_AND_TEMPLATES_GUIDE.md
**What:** Complete master reference (all formats explained)  
**Size:** ~15 KB  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/FORMATS_AND_TEMPLATES_GUIDE.md
Best: Read on GitHub (easier to navigate)
OR: Right-click → Save As to save locally
```

#### 9. NAMING_CONVENTIONS_AND_FORMATS.md
**What:** All naming rules and conventions  
**Size:** ~15 KB  
**Download:**
```
GitHub URL: https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/NAMING_CONVENTIONS_AND_FORMATS.md
Best: Read on GitHub
OR: Right-click → Save As
```

---

## 🚀 Quick Download Methods

### Method 1: Clone Entire Repository (Recommended)
Gets EVERYTHING (code + templates + examples + docs)

```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# Templates and examples now in your folder:
ls EXAMPLE_*
ls TEMPLATE_*
```

**Pros:** Get everything at once, keep it organized  
**Cons:** Larger download (~50 MB with all test data)

### Method 2: Download Individual Files
Click each file on GitHub and download

**Step by step:**
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Find file (e.g., EXAMPLE_student_answers.xlsx)
3. Click file name
4. Click "Raw" button (or download icon)
5. Right-click → Save As
6. Choose location and save

**Pros:** Get only what you need  
**Cons:** Have to download files one by one

### Method 3: Download ZIP of Entire Repo
Gets everything in one ZIP file

**Step by step:**
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Click green "Code" button (top right)
3. Select "Download ZIP"
4. Extract ZIP to your computer
5. Templates and examples are in the main folder

**Pros:** One download, everything included  
**Cons:** Need to extract ZIP file

---

## 📁 File Organization After Download

After downloading, you'll see:

```
cissp-analyzer/
├── EXAMPLE_answer_key.json          ← Download & customize
├── EXAMPLE_answer_key.csv           ← Download & customize
├── EXAMPLE_student_answers.xlsx     ← Download & customize
├── TEMPLATE_answer_key.json         ← Copy & make your own
├── TEMPLATE_student_answers.md      ← Read for guidance
├── TEMPLATE_directory_structure.md  ← Read for guidance
├── TEMPLATE_REFERENCE.txt           ← Quick overview
├── QUICK_SETUP_CARD.txt            ← Print this!
├── FORMATS_AND_TEMPLATES_GUIDE.md   ← Read for details
├── NAMING_CONVENTIONS_AND_FORMATS.md ← Read for naming rules
├── README.md                        ← Project overview
├── analyze.py                       ← Main program
├── requirements.txt                 ← Dependencies
└── ... (other files and folders)
```

---

## 🎯 Which Files to Download (By Use Case)

### Use Case 1: I Just Want to Try It
```
Download:
✅ EXAMPLE_student_answers.xlsx    (See Excel format)
✅ EXAMPLE_answer_key.json         (See JSON format)
✅ QUICK_SETUP_CARD.txt            (Follow 7 steps)

Skip everything else for now
```

### Use Case 2: I Want to Set Up My Project
```
Download:
✅ QUICK_SETUP_CARD.txt            (How to set up)
✅ TEMPLATE_directory_structure.md (Folder layout)
✅ NAMING_CONVENTIONS_AND_FORMATS.md (File naming)
✅ EXAMPLE_student_answers.xlsx    (Excel template)
✅ TEMPLATE_answer_key.json        (JSON template)

Read all 5, then create your project
```

### Use Case 3: I Want Everything
```
Clone the entire repository:
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git

You get:
✅ All templates
✅ All examples
✅ All documentation
✅ Source code
✅ Test suite
✅ Everything!
```

---

## 📥 Detailed Download Instructions

### Download EXAMPLE_student_answers.xlsx (Most Useful)

**On GitHub:**
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Look for file: `EXAMPLE_student_answers.xlsx`
3. Click the file name
4. Click "Download raw file" button (↓ icon on right)
5. File downloads to your Downloads folder
6. Open in Excel → See format → Customize for your data

**Alternative (Clone):**
```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer
open EXAMPLE_student_answers.xlsx  # On Mac
# or
start EXAMPLE_student_answers.xlsx # On Windows
```

### Download EXAMPLE_answer_key.json

**On GitHub:**
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Look for file: `EXAMPLE_answer_key.json`
3. Click the file name
4. Click "Raw" button (or download icon)
5. Right-click → Save As → Save as `.json`
6. Edit in text editor → Customize your answers
7. Save as: `exam_1_answer_key.json`

**Or Copy-Paste:**
1. Click "Raw" button
2. Select all text (Ctrl+A / ⌘A)
3. Copy (Ctrl+C / ⌘C)
4. Open text editor
5. Paste
6. Edit your data
7. Save as `.json`

### Download EXAMPLE_answer_key.csv

**On GitHub:**
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Look for file: `EXAMPLE_answer_key.csv`
3. Click the file name
4. Click "Raw" button
5. Right-click → Save As → Save as `.csv`
6. Open in Excel
7. Edit your data
8. Save

---

## ✅ Quick Links Summary

| What You Want | Click Here |
|---------------|-----------|
| Everything at once | https://github.com/sriramshiv26-prog/cissp-analyzer/archive/refs/heads/main.zip |
| Example student answers (Excel) | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_student_answers.xlsx |
| Example answer key (JSON) | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_answer_key.json |
| Example answer key (CSV) | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/EXAMPLE_answer_key.csv |
| Template answer key | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/TEMPLATE_answer_key.json |
| Quick setup guide | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/QUICK_SETUP_CARD.txt |
| Format guide | https://github.com/sriramshiv26-prog/cissp-analyzer/blob/main/FORMATS_AND_TEMPLATES_GUIDE.md |
| Repository home | https://github.com/sriramshiv26-prog/cissp-analyzer |

---

## 🔍 Can't Find the Files?

If you can't find the templates on GitHub:

### Try This:
1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Click "Code" button (green, top right)
3. Download ZIP
4. Extract ZIP
5. Look in main folder (not in subfolders)
6. Templates/examples start with `EXAMPLE_` or `TEMPLATE_`

### Files Start With:
- `EXAMPLE_` → Real working examples (30-20 questions)
- `TEMPLATE_` → Blank templates you customize
- `QUICK_SETUP_CARD.txt` → Quick reference

### Problem Solver:
```bash
# Once cloned, find all templates:
ls EXAMPLE_*
ls TEMPLATE_*

# Should show:
EXAMPLE_answer_key.csv
EXAMPLE_answer_key.json
EXAMPLE_student_answers.xlsx
TEMPLATE_answer_key.json
TEMPLATE_student_answers.md
TEMPLATE_directory_structure.md
TEMPLATE_REFERENCE.txt
QUICK_SETUP_CARD.txt
```

---

## 📱 Mobile Users

If accessing GitHub on phone:

1. Go to: https://github.com/sriramshiv26-prog/cissp-analyzer
2. Tap "Code" (green button)
3. Tap "Download ZIP"
4. Unzip on your computer later
5. Open templates in Excel/text editor

---

## 🆘 Support

**Can't download?** Check these:
- [ ] File name is correct (starts with EXAMPLE_ or TEMPLATE_)
- [ ] You're on the right GitHub page
- [ ] Internet connection is working
- [ ] Browser allows downloads
- [ ] Check Downloads folder

**File is corrupted?** Try:
1. Delete the file
2. Download again
3. Or use a different download method
4. Or clone the repository with git

---

## Summary

### To Get Templates:
1. **Easiest:** Click file on GitHub → Download raw file
2. **Fastest:** Clone repository with git
3. **Simplest:** Download ZIP from Code button

### Files to Download:
- **EXAMPLE_student_answers.xlsx** ← Most important
- **EXAMPLE_answer_key.json** ← Or CSV version
- **QUICK_SETUP_CARD.txt** ← Keep handy

### All Located At:
**https://github.com/sriramshiv26-prog/cissp-analyzer**

---

**Version:** 1.0 | **Date:** July 4, 2026 | **Status:** Live on GitHub ✅
