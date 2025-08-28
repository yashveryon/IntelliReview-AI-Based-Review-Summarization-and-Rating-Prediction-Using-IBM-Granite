import os
import traceback
from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson.natural_language_understanding_v1 import (
    NaturalLanguageUnderstandingV1,
    Features,
    SentimentOptions
)

# ✅ Load credentials from .env
load_dotenv()

# 🔑 Environment Variables
API_KEY = os.getenv("WATSON_API_KEY")
WATSON_URL = os.getenv("WATSON_URL")

# ✅ Safety check
if not API_KEY or not WATSON_URL:
    raise ValueError("❌ API key or Watson URL missing. Check your .env file.")

# ✅ Normalize IBM API Key (optional)
if API_KEY.startswith("ApiKey-"):
    print("⚠️ Detected 'ApiKey-' prefix — stripping it.")
    API_KEY = API_KEY.replace("ApiKey-", "")

# ✅ Set up IAM Authenticator
authenticator = IAMAuthenticator(API_KEY)

# ✅ Initialize Watson NLU client
nlu = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator
)
nlu.set_service_url(WATSON_URL)

# ✅ Main Sentiment Analysis Function
def analyze_sentiment_ibm(text: str) -> str:
    """
    Analyze sentiment using IBM Watson NLU.
    Returns: 'positive', 'neutral', 'negative', or 'error'
    """
    try:
        response = nlu.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions()),
            language='en'
        ).get_result()

        return response['sentiment']['document']['label']

    except ApiException as e:
        print("🔴 Watson API Error:", e.message)
        print("📄 Status Code:", e.code)
        try:
            print("📦 API Response:", e.http_response.json())
        except Exception:
            pass
        traceback.print_exc()
        return "error"

    except Exception as e:
        print("❗ Unexpected error during sentiment analysis:", str(e))
        traceback.print_exc()
        return "error"
