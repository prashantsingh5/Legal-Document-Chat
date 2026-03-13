"""
Simple Streamlit App for Legal Document Chat
Clean, minimal UI focused on functionality
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from document_extractor import DocumentExtractor
from enhanced_lease_extractor import EnhancedLeaseExtractor
from enhanced_chat_system import EnhancedChat

load_dotenv()

# Page config
st.set_page_config(page_title="Document Chat", layout="wide")

# Minimal CSS
st.markdown("""
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
.main { padding: 20px; }
h1, h2 { color: #1f77b4; }
</style>
""", unsafe_allow_html=True)

# Session state
if 'doc_extractor' not in st.session_state:
    st.session_state.doc_extractor = None
if 'chat' not in st.session_state:
    st.session_state.chat = None
if 'extracted' not in st.session_state:
    st.session_state.extracted = None

# Check API
gemini_available = os.getenv('GOOGLE_API_KEY') is not None

# Header
st.title("📄 Legal Document Chat")
st.write("Upload a lease document, extract key info, and ask questions with sources.")

# Sidebar
with st.sidebar:
    st.header("Upload")

    uploaded_file = st.file_uploader("Select PDF", type=['pdf'])

    if uploaded_file:
        temp_path = "temp_upload.pdf"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Process", use_container_width=True):
            with st.spinner("Processing..."):
                try:
                    st.session_state.doc_extractor = DocumentExtractor(temp_path)
                    st.session_state.chat = EnhancedChat(
                        st.session_state.doc_extractor,
                        use_gemini=gemini_available
                    )
                    extractor = EnhancedLeaseExtractor(
                        st.session_state.doc_extractor,
                        use_gemini=gemini_available
                    )
                    st.session_state.extracted = extractor.extract_all_fields()
                    st.success("Done!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    st.divider()

    if gemini_available:
        st.info("✅ Gemini API Connected")
    else:
        st.warning("⚠️ No Gemini API Key\n\nAdd to .env:\nGOOGLE_API_KEY=your_key")

# Main content
if not st.session_state.doc_extractor:
    st.info("👈 Upload a PDF to get started")
else:
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Chat", "Data", "Info"])

    with tab1:
        st.header("Ask Questions")

        query = st.text_input("Your question:", placeholder="What is the lease term?")

        if st.button("Search"):
            if query:
                with st.spinner("Finding answer..."):
                    answer, summary, sources = st.session_state.chat.answer_question(query)

                    st.write(answer)

                    if sources:
                        with st.expander(f"📍 Sources ({len(sources)})"):
                            for i, src in enumerate(sources, 1):
                                st.write(f"**{i}. Page {src['page']}**")
                                st.caption(src['content'][:150])

    with tab2:
        st.header("Extracted Information")

        if st.session_state.extracted:
            # Display fields
            rows = []
            for section, fields in st.session_state.extracted.items():
                if isinstance(fields, dict):
                    for field, data in fields.items():
                        if isinstance(data, dict) and data.get('found'):
                            rows.append({
                                'Section': section.replace('_', ' ').title(),
                                'Field': field.replace('_', ' ').title(),
                                'Value': str(data.get('value', ''))[:100],
                                'Source': data.get('source', '')
                            })

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)

                # Export
                col1, col2 = st.columns(2)
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button("📥 CSV", csv, "data.csv", "text/csv")
                with col2:
                    import json
                    json_str = json.dumps(st.session_state.extracted, indent=2)
                    st.download_button("📥 JSON", json_str, "data.json", "application/json")

    with tab3:
        stats = st.session_state.doc_extractor.get_document_stats()

        col1, col2, col3 = st.columns(3)
        col1.metric("Pages", stats['total_pages'])
        col2.metric("Words", f"{stats['total_words']:,}")
        col3.metric("Characters", f"{stats['total_chars']:,}")

        st.divider()

        st.subheader("Document Info")
        st.write(f"**Total Pages:** {stats['total_pages']}")
        st.write(f"**Average Page Size:** {stats['avg_page_length']:,} characters")

        # Page breakdown
        st.subheader("Pages Stats")
        pages_data = []
        for page in st.session_state.doc_extractor.pages_data:
            pages_data.append({'Page': page['page_num'], 'Size': page['length']})

        df_pages = pd.DataFrame(pages_data)
        st.bar_chart(df_pages.set_index('Page'))
