import os
import logging
import msal
import requests

logger = logging.getLogger(__name__)

CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AUTHORITY = 'https://login.microsoftonline.com/consumers'
SCOPES = ['Mail.Send']
CACHE_FILE = 'token_cache.json'
GRAPH_URL = 'https://graph.microsoft.com/v1.0/me/sendMail'

DEPT_EMAILS = {
    'Card': 'pinjarianees96@gmail.com',
    'Loan': 'shubham5411.sj@gmail.com',
    'Others': 'simran.anees.pinjari96@gmail.com',
    'Reporting': 'pinjarishakil088@gmail.com',
    'Services': 'pinjarialishan96@gmail.com'
}


def _get_access_token():
    client_id = os.getenv('AZURE_CLIENT_ID')
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache.deserialize(f.read())

    app = msal.PublicClientApplication(client_id, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()
    if not accounts:
        raise RuntimeError('Not logged in. Run `python authenticate.py` first.')

    result = app.acquire_token_silent(SCOPES, account=accounts[0])
    if cache.has_state_changed:
        with open(CACHE_FILE, 'w') as f:
            f.write(cache.serialize())

    if not result or 'access_token' not in result:
        raise RuntimeError('Token expired or invalid. Run `python authenticate.py` again.')
    return result['access_token']


def send_outlook_email(sender, text, department):
    receiver = DEPT_EMAILS.get(department, sender)
    payload = {
        'message': {
            'subject': f'Action Required: Complaint Routed to {department} Department',
            'body': {
                'contentType': 'Text',
                'content': (
                    f'Hello {department} Team,\n\n'
                    f'A new complaint has been classified and routed:\n\n"{text}"\n\n'
                    f'Please resolve within SLA.'
                ),
            },
            'toRecipients': [{'emailAddress': {'address': receiver}}],
        },
        'saveToSentItems': True,
    }
    try:
        token = _get_access_token()
        resp = requests.post(
            GRAPH_URL,
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
            json=payload,
            timeout=30,
        )
        if resp.status_code == 202:
            return True
        logger.error('Graph sendMail failed (%s): %s', resp.status_code, resp.text)
        return False
    except Exception as error:
        logger.error('Email dispatch failed: %s', error)
        return False