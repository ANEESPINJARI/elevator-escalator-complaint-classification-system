from datetime import datetime
import os
import pickle

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

from outlook_routing import send_outlook_email
from preprocessing import text_preprocessing

load_dotenv()

LABELS = ['Card', 'Loan', 'Others', 'Reporting', 'Services']
TEXT_COLUMN = 'Consumer complaint narrative'
OUTPUT_FILE = 'routed_complaints_output.xlsx'
TOKEN_CACHE_FILE = 'token_cache.json'


@st.cache_resource
def load_artifacts():
    """Load the model and tokenizer once instead of on every button click."""
    model = load_model('complaint_model.keras')
    with open('tokenizer.pkl', 'rb') as f:
        tokenizer = pickle.load(f)
    return model, tokenizer


st.set_page_config(page_title='Complaint Classifier', layout='wide')
st.title('Automated Enterprise Complaint Classification Platform')

uploaded_file = st.file_uploader('Upload Daily Complaint Excel File (.xlsx)', type=['xlsx'])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write('### Preview Uploaded Complaints', df.head())

    if TEXT_COLUMN not in df.columns:
        st.error(f"The uploaded file must contain a '{TEXT_COLUMN}' column.")
        st.stop()

    if st.button('Run AI Classification & Dispatch Outlook Emails'):
        with st.spinner('Processing Deep Learning Model & Dispatching Emails...'):
            try:
                model, tokenizer = load_artifacts()

                # ---- Classification ----
                cleaned = df[TEXT_COLUMN].apply(text_preprocessing)
                seqs = tokenizer.texts_to_sequences(cleaned)
                padded = pad_sequences(seqs, maxlen=200)

                probs = model.predict(padded)
                df['Predicted_Department'] = [LABELS[i] for i in np.argmax(probs, axis=1)]

                st.success('AI Classification Completed Successfully!')
                st.dataframe(df)

                # ---- Save locally (timestamped so an open file never blocks it) ----
                output_file = f"routed_complaints_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
                df.to_excel(output_file, index=False)
                st.success(f'Processed report saved locally as `{output_file}`')

                # ---- Send Outlook notifications (Microsoft Graph / OAuth2) ----
                sender = os.getenv('OUTLOOK_SENDER_EMAIL')

                if not sender:
                    st.warning('OUTLOOK_SENDER_EMAIL is missing from the .env file.')
                elif not os.getenv('AZURE_CLIENT_ID'):
                    st.warning('AZURE_CLIENT_ID is missing from the .env file.')
                elif not os.path.exists(TOKEN_CACHE_FILE):
                    st.warning(
                        'Outlook is not authenticated yet. Run `python authenticate.py` '
                        'once in the terminal, then try again.'
                    )
                else:
                    st.info('Dispatching Outlook emails to department mailboxes...')
                    success_count = 0
                    for _, row in df.iterrows():
                        if send_outlook_email(sender, row[TEXT_COLUMN], row['Predicted_Department']):
                            success_count += 1

                    failure_count = len(df) - success_count
                    if failure_count:
                        st.warning(
                            f'Sent {success_count} of {len(df)} emails; '
                            f'{failure_count} failed. Check the app logs for details.'
                        )
                    else:
                        st.success(f'Successfully sent all {success_count} department emails via Outlook!')

                # ---- Download button ----

                with open(output_file, 'rb') as f:
                    st.download_button(
                        'Download Processed Report (.xlsx)',
                        data=f,
                        file_name=output_file,
                    )

            except Exception as e:
                st.error(f'Processing exception: {e}')