import os
import msal
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
AUTHORITY = 'https://login.microsoftonline.com/consumers'
SCOPES = ['Mail.Send']

cache = msal.SerializableTokenCache()
app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

flow = app.initiate_device_flow(scopes=SCOPES)
if 'user_code' not in flow:
    raise SystemExit(f'Could not start login: {flow}')

print(flow['message'])  # follow the instructions: open the link and enter the code
result = app.acquire_token_by_device_flow(flow)

if 'access_token' in result:
    with open('token_cache.json', 'w') as f:
        f.write(cache.serialize())
    print('Login successful. token_cache.json saved.')
else:
    print('Login failed:', result.get('error_description'))