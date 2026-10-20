# Automated Enterprise Complaint Classification Platform

A Streamlit app that reads a daily Excel file of customer complaints, classifies each complaint into a department using a deep learning (Keras) model, and emails each complaint to the right department mailbox through Outlook (Microsoft Graph API).

**Departments:** Card, Loan, Others, Reporting, Services

## How it works

1. Upload an Excel file (`.xlsx`) with a `Consumer complaint narrative` column.
2. The text is cleaned, tokenized and passed through the model (`complaint_model.keras`).
3. A `Predicted_Department` column is added and the report is saved locally.
4. Each complaint is emailed to its department using your Outlook account.
5. You can download the processed report.

## Project structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit user interface and main workflow |
| `preprocessing.py` | Text cleaning function |
| `outlook_routing.py` | Sends emails via Microsoft Graph (OAuth2) |
| `authenticate.py` | One-time Outlook login that creates `token_cache.json` |
| `complaint_model.keras` | Trained classification model |
| `tokenizer.pkl` | Fitted tokenizer used by the model |
| `requirements.txt` | Python dependencies |
| `.env.example` | Template for your private settings |

## Setup

### 1. Clone and install

```bash
git clone https://github.com/ANEESPINJARI/elevator-escalator-complaint-classification-system.git
cd elevator-escalator-complaint-classification-system
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Register an app in Microsoft Entra (one time)

1. Go to https://entra.microsoft.com and open **App registrations > New registration**.
2. Choose an account type that includes personal Microsoft accounts.
3. Under **Authentication**, set **Allow public client flows** to **Yes**.
4. Under **API permissions**, add Microsoft Graph delegated permission **Mail.Send**.
5. Copy the **Application (client) ID**.

### 3. Create your `.env` file

Copy `.env.example` to `.env` and fill in your values:

```
OUTLOOK_SENDER_EMAIL=your-address@outlook.com
AZURE_CLIENT_ID=your-client-id
```

### 4. Log in to Outlook (one time)

```bash
python authenticate.py
```

Open the link shown, enter the code, and sign in. This creates `token_cache.json`.

### 5. Run the app

```bash
streamlit run app.py
```

## Security notes

- Never commit `.env` or `token_cache.json`. They are listed in `.gitignore`.
- `tokenizer.pkl` is a pickle file. Only load pickle files from sources you trust.
- Department email addresses are set in `outlook_routing.py`. Change them to your own.
