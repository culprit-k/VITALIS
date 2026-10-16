# Run VITALIS on a phone

VITALIS can be opened on an iPhone or Android phone through a hosted browser app. The easiest first deployment is Streamlit Community Cloud. A GitHub repository does not host a running app by itself; an authorized account owner must complete the deployment and approve the repository connection.

## Deploy the synthetic twin demo

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using the GitHub account that can access `culprit-k/VITALIS`.
2. Choose **Create app** / **Deploy an app**.
3. Select repository `culprit-k/VITALIS`, branch `main`, and main file path `dashboard/twin_demo.py`.
4. If asked for a Python version, choose Python 3.11.
5. Deploy, wait for dependency installation, and open the generated app URL in Safari or another mobile browser.
6. On iPhone, optionally use Safari's **Share → Add to Home Screen** to make a home-screen shortcut.

The repository root `requirements.txt` installs the project and its Streamlit dashboard extra. The demo uses synthetic data generated in the app; it does not require a clinical dataset, API key, or secret.

## What this deployment does and does not do

- It hosts the **synthetic adaptive-twin sandbox** for mobile interaction.
- It does not host or expose patient records.
- It does not create a trained, calibrated, clinically validated sepsis predictor.
- Its heuristic trajectory score is for software demonstration only and must not be used for diagnosis, triage, treatment, or patient-care decisions.
- Do not upload patient-level files or put credentials, clinical data, or private keys in the repository.

## If deployment fails

Check the Streamlit app's build logs first. Confirm the app points to `dashboard/twin_demo.py` on `main`, and that `requirements.txt` exists at the repository root. Share the non-sensitive error text for troubleshooting; do not share access tokens or patient information.
