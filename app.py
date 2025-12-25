import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from io import BytesIO
import time

# ========== CONFIG ==========
st.set_page_config(page_title="MRFR Related URL Finder", layout="centered")

BING_API_KEY = "PUT_YOUR_BING_API_KEY_HERE"
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

# ========== FUNCTIONS ==========
def extract_page_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        text = []
        if soup.title:
            text.append(soup.title.get_text())

        for tag in soup.find_all(["h1", "h2", "h3"]):
            text.append(tag.get_text(" ", strip=True))

        return " ".join(text)
    except:
        return ""


def extract_keywords(text, n=4):
    if not text:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=n
    )
    vectorizer.fit([text])
    return vectorizer.get_feature_names_out().tolist()


def is_valid_url(url):
    try:
        return requests.head(url, allow_redirects=True, timeout=5).status_code == 200
    except:
        return False


def find_best_related_url(keyword):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {
        "q": f"{keyword} site:marketresearchfuture.com/reports",
        "count": 10
    }

    res = requests.get(BING_ENDPOINT, headers=headers, params=params).json()

    best_url = None
    best_score = 0

    for item in res.get("webPages", {}).get("value", []):
        url = item.get("url", "")
        title = item.get("name", "").lower()

        if "/reports/" not in url:
            continue
        if not is_valid_url(url):
            continue

        score = sum(1 for w in keyword.lower().split() if w in title)

        if score > best_score:
            best_score = score
            best_url = url

    return best_url


# ========== UI ==========
st.title("🔍 MRFR Related URL Automation")
st.write("Upload Excel with **report_url** column")

file = st.file_uploader("Upload Excel", type=["xlsx"])

if file:
    df = pd.read_excel(file)

    if "report_url" not in df.columns:
        st.error("Excel must contain 'report_url'")
    else:
        if st.button("🚀 Start"):
            results = []
            progress = st.progress(0)

            urls = df["report_url"].dropna().tolist()
            total = len(urls)

            for i, report_url in enumerate(urls):
                text = extract_page_text(report_url)
                keywords = extract_keywords(text)

                for kw in keywords:
                    related = find_best_related_url(kw)
                    if related:
                        results.append({
                            "Source Report": report_url,
                            "Keyword": kw,
                            "Related URL": related
                        })

                progress.progress((i + 1) / total)
                time.sleep(0.2)

            out = pd.DataFrame(results)

            st.success("Done ✅")
            st.dataframe(out)

            buffer = BytesIO()
            out.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)

            st.download_button(
                "⬇️ Download Excel",
                buffer,
                "related_urls.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
