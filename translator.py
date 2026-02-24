import os
from dotenv import load_dotenv

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

from google.cloud import translate_v2 as translate
import time


translate_client = translate.Client()

def translate_batch(texts, source_lang="ja", target_lang="en"):
    if not texts:
        return []

    print(f"[Translate] Sending {len(texts)} items to Google Translate...")
    start = time.time()

    try:
        results = translate_client.translate(
            texts,
            source_language=source_lang,
            target_language=target_lang
        )

        translations = [r['translatedText'] for r in results]
        print(f"[Translate] Done in {time.time() - start:.2f}s")
        return translations

    except Exception as e:
        print(f"[Translate] Error: {e}")
        return ["[error]"] * len(texts)
