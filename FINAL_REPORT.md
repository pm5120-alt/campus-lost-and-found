# Final implementation report

## Delivered

- A modular, independently written Tkinter desktop project with an animated welcome page, academic project context and team details, disclaimer, animated particle field, and rotating Maliang 3D cuboid.
- Student registration/login with salted PBKDF2 password hashes, student-only signup, and one-time administrator setup protected by a local environment secret.
- SQLite item reports, input/date/image validation, private contact fields, search filters, student report list, and public browse table.
- Explainable rule-based lost/found comparisons scored from 0 to 100, with comparison reasons and persistent potential-match notices.
- Student ownership claims with private evidence, administrator-only decisions, transaction-protected conflict resolution, return marking, and persistent notifications.
- Live dashboard and administrator analytics, report review, and registered-user directory.
- Setup/readme, pinned tested dependency requirements, automated tests, third-party notices, and `.gitignore`.

## Verification performed

- `python -m compileall .` completed successfully.
- `python -m unittest discover -s tests -v` completed successfully: **8 tests passed**. Coverage includes registration/login and password checking, duplicate account and role checks, one-time environment-secret administrator setup, item reporting/search/owner isolation, rule matching, claim review and conflict handling, notifications, persistence, and data validation.
- Launched the app on the available Windows desktop using Python 3.15.0 beta and Tk 9.0. Confirmed welcome rendering, moving particles, rotating Maliang cuboid, navigation to sign-in, student registration/login, dashboard rendering, report form rendering, and a report save appearing in My Reports.
- The rotating 3D component uses a 33 ms Tkinter callback. The scene remained responsive during the visual smoke check. This is a scheduling target, not an instrumented FPS benchmark.
- Installed and imported Maliang 3.2.0 with maliang-three 1.0.4. The 3D extension is optional at runtime; the app falls back to its own rotating Canvas cube if import or setup fails.

## Known limitations

- The workspace only provides Python 3.15.0 beta. The dependency packages installed and the GUI worked here, but a stable Python 3.11–3.14 runtime was not available for cross-version verification.
- The visual GUI smoke check covered the welcome, sign-in/registration, dashboard, and report submission paths. The administrator screens and full claim decision path were verified through automated service tests, not manually exercised in the GUI.
- This is a single-computer local prototype. It has no SRM single sign-on, shared campus server, remote notifications, deployment, or multi-computer synchronization.
- The first administrator setup requires the operator to set `CAMPUS_ADMIN_SETUP_TOKEN` before launching the app. Keep the project folder and SQLite database on a trusted machine.
- Uploaded images are validated and stored locally, but there is no in-app image preview. Students can view their own reports and compare matches; editing or withdrawing a submitted report is not implemented.
- Administrator review supports claim decisions and marking a report returned. It does not include a full report rejection/moderation queue or account disable controls; the user directory is read-only.
- Login/register screens change directly; animated panel transitions and a password visibility toggle are not implemented. Notifications are persisted and displayed but do not yet have a read/unread control.
- Similarity scores are heuristic prompts for human review, not machine learning, proof of ownership, or automatic approval.

## Run

From the project folder, install Python 3.11+ with Tcl/Tk, run `python -m pip install -r requirements.txt`, then `python app.py`. The first administrator is created from **First-time administrator setup** on the sign-in page. Run the two verification commands above to execute the local checks.
