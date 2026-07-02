# UiPath Orchestrator Django Project - Pure Offline Setup

## Step 1: Download All Packages (requires internet once)

Use this command on a machine with internet:
```bash
pip download Django==4.2.0 mssql-django==1.0.2 pyodbc==4.0.37 python-decouple==3.8 requests==2.31.0 -d packages/
```

This creates a `packages/` folder with all .whl files and dependencies.

## Step 2: Transfer to Offline Machine

Copy the entire `packages/` folder to your target machine (USB drive, network share, etc.)

## Step 3: Install ODBC Driver (One-time, requires download once)

**Windows:**
1. Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Download `msodbcsql.msi` (offline installer)
3. Run: `msodbcsql.msi` → Accept → Install
4. Verify: Open `odbcad32.exe` → should see driver listed

## Step 4: Install Python Packages (Offline)

```bash
# Navigate to packages folder
cd packages

# Install all packages offline
pip install Django-4.2.0-py3-none-any.whl
pip install mssql_django-1.0.2-py3-none-any.whl
pip install pyodbc-4.0.37-cp311-cp311-win_amd64.whl
pip install python_decouple-3.8-py3-none-any.whl
pip install requests-2.31.0-py3-none-any.whl
```

## Step 5: Verify Installation

```bash
python -c "import django; print(django.get_version())"
python -c "import pyodbc; print('pyodbc OK')"
python -c "import mssql; print('mssql-django OK')"
```

All done! No internet needed from here on.
