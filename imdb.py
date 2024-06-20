import os
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from gtts import gTTS
import tempfile
import os

st.set_page_config(layout="wide", page_title="IMDB Movies Dashboard")

file_path = 'imdb50.csv' 
data = pd.read_csv(file_path)

def text_to_speech_gtts(text, lang='id'):
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tts.save(tmpfile.name)
        return tmpfile.name

def clean_monetary_value(value):
    try:
        return float(value.replace('$', '').replace(',', '').replace('¥', '').replace('£', '').replace('€', ''))
    except:
        return None
    
def clean_color(value):
    value = str(value).strip().lower()
    if 'color' in value:
        return 'Color'
    elif 'black and white' in value or 'bw' in value:
        return 'Black and White'
    else:
        return Value
data['Color'] = data['Color'].apply(clean_color)
data = data[data['Color'].notnull()]

def format_number(number):
    if isinstance(number, str):
        number = float(number.replace(',', ''))
    if number >= 10**9:
        return f"{number / 10**9:.2f}B"
    elif number >= 10**6:
        return f"{number / 10**6:.2f}M"
    elif number >= 10**3:
        return f"{number / 10**3:.1f}K"
    else:
        return f"{number:.2f}"

data['Budget'] = data['Budget'].apply(clean_monetary_value)
data['Gross US & Canada'] = data['Gross US & Canada'].apply(clean_monetary_value)
data['Opening weekend Earnings'] = data['Opening weekend Earnings'].apply(clean_monetary_value)
data['Gross worldwide'] = data['Gross worldwide'].apply(clean_monetary_value)
data['Runtime (minutes)'] = data['Runtime'].str.extract('(\d+)').astype(float)
data['Opening weekend Release Date'] = pd.to_datetime(data['Opening weekend Release Date'], errors='coerce')

color_palette = ['#003f5c', '#58508d', '#bc5090', '#ff6361', '#ffa600']

total_titles = data['Title'].nunique()
total_budget = data['Budget'].sum()
total_opening_weekend_earnings = data['Opening weekend Earnings'].sum()
total_gross_worldwide = data['Gross worldwide'].sum()

st.title('Analisis Dataset Film IMDB')

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Titles", value=format_number(total_titles))
col2.metric(label="Total Budget", value=f"${format_number(total_budget)}")
col3.metric(label="Total Opening Weekend Earnings", value=f"${format_number(total_opening_weekend_earnings)}")
col4.metric(label="Total Gross Worldwide", value=f"${format_number(total_gross_worldwide)}")

st.markdown("""
            <div style='text-align: justify;'>
                    Berdasarkan analisis data penjualan Adventure Works dari tahun 2001 hingga 2004, terlihat tren peningkatan yang signifikan dalam kinerja penjualan perusahaan. Total penjualan meningkat dari 3,27 juta USD pada tahun 2001 menjadi 9,77 juta USD pada tahun 2004, yang menunjukkan pertumbuhan lebih dari tiga kali lipat dalam empat tahun. Kuantitas produk yang terjual juga meningkat secara konsisten setiap tahun, dari 1,0 ribu unit pada tahun 2001 menjadi 32,3 ribu unit pada tahun 2004. Meskipun total penjualan dan kuantitas meningkat, profit tetap stabil dengan sedikit penurunan dari 4,07 juta USD pada tahun 2003 menjadi 4,05 juta USD pada tahun 2004. Persentase keuntungan relatif stabil dengan sedikit fluktuasi, menunjukkan efisiensi operasional yang baik. Margin keuntungan tetap kuat di sekitar 40%, mencerminkan kemampuan perusahaan untuk mempertahankan profitabilitas yang tinggi meskipun ada peningkatan dalam volume penjualan. Data ini menunjukkan performa yang mengesankan dan pertumbuhan yang berkelanjutan dari Adventure Works.
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"<p style='padding-top: 8px;'></p>", unsafe_allow_html=True)
if st.button("Convert to Speech"):
   text = f"Berdasarkan analisis data penjualan Adventure Works dari tahun dua ribu satu hingga dua ribu empat, terlihat tren peningkatan yang signifikan dalam kinerja penjualan perusahaan. Total penjualan meningkat dari tiga koma dua tujuh juta USD pada tahun dua ribu satu menjadi sembilan koma tujuh tujuh juta USD pada tahun dua ribu empat, yang menunjukkan pertumbuhan lebih dari tiga kali lipat dalam empat tahun. Kuantitas produk yang terjual juga meningkat secara konsisten setiap tahun, dari satu koma nol ribu unit pada tahun dua ribu satu menjadi tiga puluh dua koma tiga ribu unit pada tahun dua ribu empat. Meskipun total penjualan dan kuantitas meningkat, profit tetap stabil dengan sedikit penurunan dari empat koma nol tujuh juta USD pada tahun dua ribu tiga menjadi empat koma nol lima juta USD pada tahun dua ribu empat. Persentase keuntungan relatif stabil dengan sedikit fluktuasi, menunjukkan efisiensi operasional yang baik. Margin keuntungan tetap kuat di sekitar empat puluh persen, mencerminkan kemampuan perusahaan untuk mempertahankan profitabilitas yang tinggi meskipun ada peningkatan dalam volume penjualan. Data ini menunjukkan performa yang mengesankan dan pertumbuhan yang berkelanjutan dari Adventure Works."
   audio_file = text_to_speech_gtts(text, lang='id')
   st.audio(audio_file)
   os.remove(audio_file)

col1, col2 = st.columns(2)

with col1:
    # Top 10 Movies by Gross Worldwide (Horizontal Bar Chart)
    top10_gross = data.nlargest(10, 'Gross worldwide').sort_values(by='Gross worldwide', ascending=True)
    fig3 = px.bar(top10_gross, x='Gross worldwide', y='Title', orientation='h', title='Top 10 Movies by Gross Worldwide', color_discrete_sequence=color_palette)
    fig3.update_layout(xaxis_title='Gross worldwide($)', yaxis_title='Movie Title')
    st.plotly_chart(fig3, use_container_width=True)

    # Line Chart of Opening Weekend Earnings Over Time
    data_sorted = data.sort_values(by='Opening weekend Release Date')
    fig_opening_weekend_earnings = alt.Chart(data_sorted).mark_line().encode(
        x='Opening weekend Release Date:T',
        y='Opening weekend Earnings:Q',
        tooltip=['Title', 'Opening weekend Earnings']
    ).properties(title='Opening Weekend Earnings Over Time')
    st.altair_chart(fig_opening_weekend_earnings, use_container_width=True)

    #Top 10 Budget
    top10_budget = data.nlargest(10, 'Budget').sort_values(by='Budget', ascending=True)
    fig = px.bar(top10_budget, x='Budget', y='Title', orientation='h', 
                title='Top 10 Highest Budget Movies', 
                color_discrete_sequence=['#003f5c'])

    fig.update_layout(xaxis_title='Budget ($)', yaxis_title='Movie Title')
    st.plotly_chart(fig, use_container_width=True)

    #HeatMap
    fig = px.density_heatmap(data, x='Gross US & Canada', y='Gross worldwide', title='Heatmap of Gross US & Canada vs. Gross Worldwide')
    fig.update_layout(xaxis_title='Gross US & Canada ($)', yaxis_title='Gross Worldwide ($)')
    st.plotly_chart(fig, use_container_width=True)

    # Runtime Distribution (Box Plot)
    fig2 = px.box(data, y='Runtime (minutes)', title='Movies Duration Distribution', color_discrete_sequence=color_palette)
    fig2.update_layout(yaxis_title='Duration')
    st.plotly_chart(fig2, use_container_width=True)

    # Pie Chart of Color Distribution
    color_counts = data['Color'].value_counts()
    fig_color_distribution = px.pie(values=color_counts.values, names=color_counts.index, title='Pie Chart of Color Distribution')
    st.plotly_chart(fig_color_distribution, use_container_width=True)

with col2:
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 10px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                    Grafik ini menunjukkan bahwa Amerika Serikat dan Australia konsisten sebagai dua negara dengan total penjualan tertinggi. Pada tahun 2001, Australia memimpin dengan total penjualan sekitar 1,2 juta, diikuti oleh Amerika Serikat. Tren ini berlanjut hingga tahun 2002 dengan peningkatan yang signifikan di Amerika Serikat, menyusul Australia di posisi kedua. Pada tahun 2003, meskipun posisi puncak dipegang oleh Australia, Amerika Serikat berhasil mendekati dengan peningkatan penjualan yang signifikan. Pada tahun 2004, Amerika Serikat mencapai puncak penjualan tertinggi dengan total lebih dari 3 juta, sementara Australia turun ke posisi kedua. Hal ini menunjukkan pertumbuhan pasar yang signifikan di Amerika Serikat, yang menjadi pasar utama Adventure Works dalam periode ini, dengan peningkatan yang konsisten setiap tahun. Adapun negara-negara seperti Inggris, Jerman, dan Perancis, meskipun berkontribusi pada penjualan, tetap berada di posisi lebih rendah dengan total penjualan lebih sedikit.
                </div>
                """, unsafe_allow_html=True)
