import re

def text_preprocessing(complaint):
    complaint = str(complaint).lower()
    complaint = re.sub(r"[x]{2,}", "", complaint)
    complaint = re.sub(r"[^a-z0-9\s]", "", complaint)
    return complaint