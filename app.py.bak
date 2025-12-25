import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import time
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(page_title="MRFR Keyword Automation", layout="centered")

# ---------------- FUNCTIONS ----------------
def extract_page_text(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        html = requests.get(url, headers=headers, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")

        text_parts = []

        # 1️⃣ Title
        if soup.title:
            text_parts.append(soup.title.get_text(strip=True))

        # 2️⃣ Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            text_parts.append(meta_desc["content"])

        # 3️⃣ Headings (H1-H3)
        for tag in soup.find_all(["h1", "h2", "h3"]):
            t = tag.get_text(" ", strip=True)
            if len(t) > 5:
                text_parts.append(t)

        # 4️⃣ Body text fallback
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        body_text = soup.get_text(" ", strip=True)
        if len(body_text) > 500:
            text_parts.append(body_text)

        final_text = " ".join(text_parts)
        return final_text

    except Exception as e:
        return ""


def extract_keywords(text, top_n=4):
    if not text or len(text) < 100:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=top_n
    )
    vectorizer.fit([text])
    return vectorizer.get_feature_names_out().tolist()


def search_dummy(keyword):
    base = "https://www.marketresearchfuture.com/reports/"
    return [
        f"{base}{keyword.replace(' ', '-')}-market",
        f"{base}{keyword.replace(' ', '-')}-industry"
    ]


def is_relevant(url):
    return "marketresearchfuture.com/reports" in url.lower()


# ---------------- UI ----------------
st.title("📊 MRFR Keyword & Hyperlink Automation")
st.write("Upload Excel with **report_url** column")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "report_url" not in df.columns:
        st.error("Excel must contain a column named: report_url")
    else:
        st.success("File uploaded successfully")

        if st.button("🚀 Start Automation"):
            progress = st.progress(0)
            results = []

            urls = df["report_url"].dropna().tolist()
            total = len(urls)

            for i, report_url in enumerate(urls):
                text = extract_page_text(report_url)

                # DEBUG (keep for now)
                st.write("TEXT LENGTH:", len(text))

                keywords = extract_keywords(text)
                st.write("KEYWORDS:", keywords)

                # 🚨 GUARANTEED fallback
                if not keywords:
                    keywords = ["market analysis", "industry overview", "forecast", "growth"]

                for kw in keywords:
                    for rurl in search_dummy(kw):
                        if is_relevant(rurl):
                            results.append({
                                "Source Report": report_url,
                                "Keyword": kw,
                                "Related URL": rurl
                            })

                progress.progress((i + 1) / total)
                time.sleep(0.2)

            output_df = pd.DataFrame(results)

            st.success("✅ Automation completed")
            st.dataframe(output_df)

            excel_buffer = BytesIO()
            output_df.to_excel(excel_buffer, index=False, engine="openpyxl")
            excel_buffer.seek(0)

            st.download_button(
                label="⬇️ Download Excel",
                data=excel_buffer,
                file_name="mrf_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
