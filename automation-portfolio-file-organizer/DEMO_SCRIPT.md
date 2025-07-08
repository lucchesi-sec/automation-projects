# Demo Script: File Organizer

## 🎬 Project Demonstration Guide

### Demo Overview
This script provides a structured walkthrough of the File Organizer project, highlighting key features and capabilities.

### Pre-Demo Setup
1. Ensure Python 3.8+ is installed
2. Install project dependencies: `pip install -r requirements.txt`
3. Prepare sample files in a test directory
4. Have target organization directory ready

### Demo Flow (5-7 minutes)

#### 1. Problem Introduction (1 minute)
**Talking Points:**
- "Everyone has cluttered download folders and messy file systems"
- "Manual organization is time-consuming and error-prone"
- "This tool automates intelligent file organization"

#### 2. Basic Usage Demo (2 minutes)
```bash
# Show the command structure
python -m src.file_organizer --help

# Run basic organization
python -m src.file_organizer --source ./demo/messy --target ./demo/organized
```

**Show Results:**
- Files categorized by type (documents, images, code, etc.)
- Duplicate detection and handling
- Comprehensive logging output

#### 3. Advanced Features (2 minutes)
```bash
# Custom rules demonstration
python -m src.file_organizer --config custom_rules.yaml --source ./demo/advanced

# Batch processing
python -m src.file_organizer --batch --recursive --source ./demo/multiple_dirs
```

**Highlight:**
- Custom organization rules
- Recursive directory processing
- Performance with large file sets