# Campus Lost & Found Management System

A Python/Tkinter desktop prototype for campus lost-and-found reports, possible matches, ownership claims, and administrator review. This is a student project, not an official SRMIST service.

## Get the project

Clone the repository and open PowerShell in its folder:

```powershell
git clone https://github.com/pm5120-alt/campus-lost-and-found.git
cd campus-lost-and-found
```

Alternatively, on GitHub click **Code → Download ZIP**, extract the downloaded repository, and open PowerShell in the extracted `campus-lost-and-found` folder.

## Run on Windows 10/11

Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/). During setup, enable **Add Python to PATH** and include **Tcl/Tk and IDLE**.

Run these commands in PowerShell from the repository folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

The animated welcome screen opens first. Click **ENTER APPLICATION** to reach sign-in and registration.

## First-time administrator setup

Do this once on the trusted computer that will store the app's local database. In the same PowerShell window, generate a private one-time setup code and start the app:

```powershell
$setupCode = (python -c "import secrets; print(secrets.token_urlsafe(32))").Trim()
$env:CAMPUS_ADMIN_SETUP_TOKEN = $setupCode
python app.py
```

In the app, click **ENTER APPLICATION**, then **First-time administrator setup**. Enter the value of `$setupCode` when prompted, choose an administrator username, and set a password with at least 10 characters including a letter and a number. Then sign in with those credentials.

After the administrator is created, the setup code is no longer needed. Close the app and clear it from the current PowerShell session:

```powershell
Remove-Item Env:CAMPUS_ADMIN_SETUP_TOKEN
```

For later launches, activate `.venv` and run `python app.py`. No setup token is required after the administrator has been created.

## Student accounts

On the sign-in page, choose **Create a student account**, enter a username and password, and sign in. Student signup cannot create administrator accounts.

## Run tests

With the virtual environment active:

```powershell
python -m compileall .
python -m unittest discover -s tests -v
```

The service test suite currently passes **8 tests**. `FINAL_REPORT.md` documents the verification scope and known limitations.

## Data and security notes

The app stores data locally in `data/campus_lost_found.sqlite3` and images in `uploads/`. These runtime files are excluded from version control and are not synchronized across computers. Keep the project folder on a trusted device, back up the local `data` folder carefully, and never commit actual user reports, contact details, uploaded images, databases, passwords, or administrator setup codes.

This is a single-computer academic prototype. It does not provide campus SSO, a shared server, multi-computer synchronization, or production hosting. Similarity matches are heuristic suggestions, not machine-learning predictions or proof of ownership.

## Credits

The optional animated 3D welcome scene uses Maliang and maliang-three. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for license information.
