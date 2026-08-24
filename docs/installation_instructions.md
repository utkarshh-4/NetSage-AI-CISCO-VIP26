# Installation Instructions

## Prerequisites

Before installing NetSage AI, ensure you have the following:

### Required Software

- **Python 3.11 or higher**: The project requires Python 3.11+ for all features
- **pip package manager**: For installing Python dependencies
- **Git**: For cloning the repository (optional, can download directly)

### Optional Software

- **OpenAI API key**: Required for AI diagnosis features
- **Virtual environment**: Recommended for Python dependency isolation

## Installation Steps

### Step 1: Clone or Download the Repository

**Option A: Clone with Git**

```bash
git clone <repository-url>
cd CISCO-VIP26
```

**Option B: Download ZIP**

1. Download the repository as a ZIP file
2. Extract the ZIP file
3. Navigate to the extracted directory

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
```

**Linux/Mac:**
```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your command prompt indicating the virtual environment is active.

### Step 4: Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install:
- pandas>=2.0.0
- python-dotenv>=1.0.0
- pydantic>=2.0.0
- openai>=1.0.0
- streamlit>=1.28.0
- plotly>=5.17.0
- pytest>=7.4.0
- pytest-cov>=4.1.0
- black>=23.0.0
- flake8>=6.0.0
- mypy>=1.5.0

### Step 5: Set Up Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit the `.env` file with your OpenAI API key:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_actual_api_key_here

# Optional: Model selection (default: gpt-3.5-turbo)
OPENAI_MODEL=gpt-3.5-turbo

# Optional: Skip AI diagnosis and use rule-based analysis only
SKIP_AI=false
```

**Important Notes**:
- Never commit `.env` to version control
- Keep your API key secure
- You can run without AI features by setting `SKIP_AI=true`

### Step 6: Verify Installation

Run the test suite to verify everything is installed correctly:

```bash
pytest tests/
```

All 170 tests should pass.

### Step 7: (Optional) Install Development Tools

If you plan to contribute to the project, install development tools:

```bash
pip install black flake8 mypy
```

## Troubleshooting Installation

### Issue: Python Version Too Old

**Error**: `SyntaxError` or version-related errors

**Solution**: Upgrade Python to 3.11 or higher
```bash
# Download from python.org
# Use pyenv (Linux/Mac)
# Use python launcher (Windows)
```

### Issue: Virtual Environment Creation Fails

**Error**: `Error: Command '['...']' returned non-zero exit status`

**Solution**: Ensure you have write permissions and Python is properly installed

### Issue: pip Install Fails

**Error**: `Could not find a version that satisfies the requirement`

**Solution**: Upgrade pip first
```bash
python -m pip install --upgrade pip
```

### Issue: OpenAI API Key Issues

**Error**: `AuthenticationError` or quota exceeded

**Solution**: 
- Verify your API key is correct
- Check your OpenAI account quota
- Set `SKIP_AI=true` to use rule-based analysis only

### Issue: Streamlit Import Error

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**: Ensure virtual environment is activated and dependencies installed
```bash
# Verify activation
pip list | grep streamlit

# Reinstall if needed
pip install streamlit>=1.28.0
```

## Installation Verification

### Quick Verification

Run these commands to verify installation:

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Run test suite
pytest tests/ -v

# Try importing main modules
python -c "from data.data_loader import load_cases; print('Data loader OK')"
python -c "from rules.checker import run_all_checks; print('Rule checker OK')"
python -c "from ai.diagnose import AIDiagnosisEngine; print('AI engine OK')"
python -c "from review.review_manager import ReviewManager; print('Review manager OK')"
```

### Expected Output

- Python version: 3.11.x or higher
- All required packages in pip list
- All 170 tests pass
- All module imports succeed

## Alternative Installation Methods

### System-Wide Installation (Not Recommended)

You can install dependencies system-wide, but this is not recommended:

```bash
pip install -r requirements.txt
```

**Warning**: This may conflict with other Python projects on your system.

### Using conda

If you use conda:

```bash
conda create -n netsage-ai python=3.11
conda activate netsage-ai
pip install -r requirements.txt
```

## Post-Installation Configuration

### Configure Streamlit

The `.streamlit/config.toml` file contains Streamlit configuration:

```toml
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
```

You can customize this file to change the appearance of the dashboard.

### Configure Git Ignore

The `.gitignore` file excludes:
- `venv/` (virtual environment)
- `.env` (API keys)
- `__pycache__/` (Python cache)
- `*.pyc` (compiled Python)
- `.pytest_cache/` (pytest cache)
- `validation_results/` (generated results)

## Installation Summary

After successful installation, you should have:

- ✅ Python 3.11+ installed
- ✅ Virtual environment created and activated
- ✅ All dependencies installed
- ✅ Environment variables configured
- ✅ Test suite passing (170/170)
- ✅ All modules importable

You are now ready to use NetSage AI!

## Next Steps

1. **Run the Dashboard**: See Application Usage Instructions
2. **Run Tests**: See Testing Instructions
3. **Run Demo**: See Demo Instructions
4. **Read Documentation**: See Architecture Documentation