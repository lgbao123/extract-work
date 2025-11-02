# 🚀 Setup Instructions

## Prerequisites

✅ **Python 3.8+** installed
✅ **pip** package manager
✅ **Google Cloud Project** with Sheets API enabled

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `pandas` - Data manipulation
- `openpyxl` - Excel file reading
- `python-dotenv` - Environment variables
- `gspread` - Google Sheets API
- `gspread-dataframe` - DataFrame integration
- `google-auth` - Authentication

---

## Step 2: Set Up Google Sheets API

### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project name

### 2.2 Enable Google Sheets API

1. In Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click **Enable**
4. Also enable "Google Drive API"

### 2.3 Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Fill in details:
   - **Service account name**: `work-report-service`
   - **Service account ID**: (auto-generated)
   - **Description**: "Service account for work report automation"
4. Click **Create and Continue**
5. Grant role: **Editor** (or custom role with Sheets access)
6. Click **Done**

### 2.4 Download Credentials JSON

1. In **Credentials** page, find your service account
2. Click on the service account name
3. Go to **Keys** tab
4. Click **Add Key** → **Create new key**
5. Choose **JSON** format
6. Click **Create**
7. JSON file will be downloaded (e.g., `project-name-xxxxx.json`)
8. **Rename** this file to `credentials.json`
9. **Move** it to your project root directory:
   ```
   C:\Users\Bao\Desktop\Work\App\report_task\credentials.json
   ```

### 2.5 Find Service Account Email

Open `credentials.json` and find the email:
```json
{
  "client_email": "work-report-service@project-name.iam.gserviceaccount.com",
  ...
}
```

Copy this email address - you'll need it in the next step.

---

## Step 3: Set Up Google Spreadsheet

### 3.1 Create Spreadsheet

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Name it: **Work Report Database** (or your preferred name)

### 3.2 Share with Service Account

**IMPORTANT:** This step is required!

1. In your spreadsheet, click **Share** button (top right)
2. Paste the service account email from Step 2.5
3. Set permission to **Editor**
4. **Uncheck** "Notify people" (service accounts don't receive emails)
5. Click **Share**

### 3.3 Get Spreadsheet ID

Look at your spreadsheet URL:
```
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        This is your SPREADSHEET_ID
```

Copy the ID between `/d/` and `/edit`.

---

## Step 4: Configure Environment

### 4.1 Edit `.env` File

Open `.env` in your project root and update:

```env
# Required: Path to credentials file (keep as is if you named it credentials.json)
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# Required: Paste your spreadsheet ID here
GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms

# Optional: Or use spreadsheet name (leave ID empty if using this)
GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database

# Optional settings
DEBUG=False
LOG_LEVEL=INFO
AUTO_UPDATE=False
```

### 4.2 Verify File Structure

Your project should look like:
```
report_task/
├── .env                    ← Configuration file (YOU EDIT THIS)
├── credentials.json        ← Google credentials (YOU ADD THIS)
├── main.py                ← Entry point
├── requirements.txt       ← Dependencies
├── config/                ← Configuration modules
├── models/                ← Data models
├── parsers/               ← Excel parsing
├── repositories/          ← Data access
├── services/              ← Business logic
├── utils/                 ← Utilities
└── input/                 ← Put your Excel files here
```

---

## Step 5: Test Connection

Run the test script to verify everything is set up correctly:

```bash
python test_connection.py
```

Expected output:
```
✓ Connected to Google Sheets: Work Report Database
✓ All sheets initialized
✓ Connection test successful!
```

If you see errors:
- ❌ **Credentials file not found**: Check `credentials.json` exists
- ❌ **Permission denied**: Make sure you shared spreadsheet with service account
- ❌ **Spreadsheet not found**: Check your `GOOGLE_SHEETS_SPREADSHEET_ID` in `.env`

---

## Step 6: First Import

Now you're ready to import your first report!

```bash
python main.py import \
  --file "input/your_report.xlsx" \
  --employee "NV001" \
  --department "IT"
```

### Command Explanation:
- `import` - Command to import a report
- `--file` - Path to your Excel file
- `--employee` - Employee code (will be created if doesn't exist)
- `--department` - Department code

### Expected Output:
```
✓ Connected to Google Sheets

📄 Processing file: input/your_report.xlsx
✓ Success: created report RPT-NV001-202409
  → Period: 2024-09
  → Total tasks: 45
  → Task breakdown:
    - actual_functional: 12
    - actual_project: 8
    - planned_functional: 15
    - planned_project: 10

✓ Complete
```

---

## Troubleshooting

### Issue: "Credentials file not found"
**Solution:** 
1. Ensure `credentials.json` is in project root
2. Check `.env` has correct path: `GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json`

### Issue: "Permission denied" or "Forbidden"
**Solution:**
1. Open your Google Spreadsheet
2. Click **Share**
3. Add the service account email (from `credentials.json`)
4. Grant **Editor** permission

### Issue: "Spreadsheet not found"
**Solution:**
1. Check spreadsheet ID in `.env` is correct
2. Ensure spreadsheet is shared with service account
3. Try using spreadsheet name instead:
   - Set `GOOGLE_SHEETS_SPREADSHEET_ID=` (empty)
   - Set `GOOGLE_SHEETS_SPREADSHEET_NAME=Your Exact Spreadsheet Name`

### Issue: "Module not found"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Excel parsing errors
**Solution:**
1. Verify Excel file format matches expected structure
2. Check file has required sections:
   - "1. Công việc theo chức năng"
   - "2. Công việc theo dự án"
   - "II. KẾ HOẠCH CÔNG VIỆC"

---

## Quick Reference

### View Help
```bash
python main.py --help
```

### Import Commands
```bash
# Single import
python main.py import -f "file.xlsx" -e "NV001" -d "IT"

# Update existing
python main.py import -f "file.xlsx" -e "NV001" -d "IT" --auto-update

# Batch import
python main.py batch -f "r1.xlsx" "r2.xlsx" -e "NV001" "NV002" -d "IT" "HR"
```

### View Commands
```bash
# View report
python main.py view -r "RPT-NV001-202409"

# Validate data
python main.py validate
```

---

## Security Notes

⚠️ **Important:**

1. **Never commit `credentials.json`** to Git
   - It's already in `.gitignore`
   - This file contains sensitive credentials

2. **Never commit `.env`** with real values to Git
   - Use `.env.example` for templates
   - Each developer should have their own `.env`

3. **Limit service account permissions**
   - Only grant access to required spreadsheets
   - Use custom roles if possible

4. **Rotate credentials regularly**
   - Download new JSON key every few months
   - Delete old keys in Google Cloud Console

---

## Next Steps

Once setup is complete:

1. ✅ Read [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed usage
2. ✅ Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for code examples
3. ✅ See [RESTRUCTURING_FINAL.md](RESTRUCTURING_FINAL.md) for architecture overview

---

**Need Help?**

Check the logs:
```bash
tail -f logs/app.log
```

Enable debug mode in `.env`:
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

---

## Summary Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Google Cloud Project created
- [ ] Google Sheets API enabled
- [ ] Service Account created
- [ ] `credentials.json` downloaded and placed in project root
- [ ] Google Spreadsheet created
- [ ] Spreadsheet shared with service account email (Editor permission)
- [ ] `.env` file created and configured with spreadsheet ID
- [ ] Test connection successful (`python test_connection.py`)
- [ ] First import successful

✅ **All done! You're ready to use the system!**
