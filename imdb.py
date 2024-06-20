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
        return None
data['Color'] = data['Color'].apply(clean_color)

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
                   Dashboard ini menampilkan performa finansial dari 50 film teratas berdasarkan data dari situs IMDB. Total anggaran produksi untuk 50 film ini mencapai $2,14 miliar, yang menunjukkan skala besar investasi dalam industri film. Dari total anggaran tersebut, film-film ini berhasil meraih pendapatan kotor global sebesar $15,61 miliar, yang menandakan laba yang sangat menguntungkan. Selain itu, pendapatan total pada akhir pekan pembukaan dari 50 film ini mencapai $825,62 juta, mencerminkan antusiasme dan minat yang besar dari penonton.
            """, unsafe_allow_html=True)

st.markdown(f"<p style='padding-top: 8px;'></p>", unsafe_allow_html=True)
if st.button("Convert to Speech"):
   text = f"Dashboard ini menampilkan performa finansial dari 50 film teratas berdasarkan data dari situs IMDB. Total anggaran produksi untuk 50 film ini mencapai $2,14 miliar, yang menunjukkan skala besar investasi dalam industri film. Dari total anggaran tersebut, film-film ini berhasil meraih pendapatan kotor global sebesar $15,61 miliar, yang menandakan laba yang sangat menguntungkan. Selain itu, pendapatan total pada akhir pekan pembukaan dari 50 film ini mencapai $825,62 juta, mencerminkan antusiasme dan minat yang besar dari penonton.."
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
                Grafik ini menampilkan 10 film teratas berdasarkan pendapatan kotor di seluruh dunia. Terlihat bahwa "The Lord of the Rings: The Return of the King" menduduki peringkat pertama dengan pendapatan tertinggi, diikuti oleh "The Dark Knight" dan "The Lion King". Film-film dari franchise "The Lord of the Rings" menempati tiga posisi dalam daftar ini, menunjukkan popularitas dan kesuksesan besar dari seri tersebut. Film-film lain yang masuk dalam daftar termasuk "Inception", "Star Wars", "Interstellar", "Dune: Part Two", dan "Forrest Gump", yang semuanya juga menunjukkan performa luar biasa di box office global. Data ini mencerminkan daya tarik yang kuat dari film-film blockbuster dengan tema epik dan fantastik di kalangan penonton internasional.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 100px;'></p>", unsafe_allow_html=True)
    st.subheader("Opening Weekend Earnings Over Time")
    st.markdown("""
                <div style='text-align: justify;'>
                Grafik ini menunjukkan pendapatan akhir pekan pembukaan film dari waktu ke waktu, mulai dari tahun 1975 hingga 2020. Terlihat bahwa pendapatan akhir pekan pembukaan film secara umum mengalami peningkatan signifikan sejak akhir 1980-an hingga awal 2000-an. Puncak tertinggi terjadi sekitar tahun 2010, dengan pendapatan mendekati $160 juta pada akhir pekan pembukaannya. Setelah itu, terdapat fluktuasi yang cukup tajam dengan beberapa periode penurunan dan kenaikan kembali. Tren ini mencerminkan bagaimana industri film telah berkembang pesat, dengan peningkatan anggaran pemasaran dan produksi, serta antisipasi penonton yang semakin tinggi terhadap film-film baru.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 130px;'></p>", unsafe_allow_html=True)
    st.subheader("Highest Budget Movies")
    st.markdown("""
                <div style='text-align: justify;'>
                Grafik ini menampilkan film-film dengan anggaran produksi terbesar, menunjukkan tren bahwa film dengan tema epik, sci-fi, dan aksi membutuhkan investasi besar untuk menciptakan pengalaman sinematik yang memukau. Anggaran besar ini mencakup biaya untuk efek visual canggih, lokasi yang luas, dan tim produksi yang besar, yang semuanya berkontribusi pada kualitas dan daya tarik film tersebut. Investasi besar ini juga mencerminkan ekspektasi tinggi terhadap kesuksesan box office, di mana film-film ini diharapkan tidak hanya memikat penonton dengan visual spektakuler tetapi juga meraih pendapatan yang signifikan. Tren ini memperlihatkan bagaimana industri film berani mengambil risiko besar demi menghasilkan karya-karya unggulan.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 140px;'></p>", unsafe_allow_html=True)
    st.subheader("Gross US & Canada vs. Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                Heatmap ini memvisualisasikan hubungan antara pendapatan kotor di AS & Kanada dengan pendapatan kotor di seluruh dunia untuk kumpulan data film. Intensitas warna menunjukkan jumlah film yang jatuh ke dalam setiap kelompok pendapatan. Dari heatmap ini, terlihat bahwa sejumlah besar film meraup antara $200 juta dan $600 juta di AS & Kanada, dan film-film tersebut cenderung meraup antara $0,6 miliar dan $1,2 miliar di seluruh dunia, seperti yang ditunjukkan oleh area biru gelap di tengah. Warna yang lebih terang pada kelompok pendapatan yang lebih rendah menunjukkan lebih sedikit film yang mencapai pendapatan kotor tinggi di seluruh dunia meskipun pendapatan domestik rendah. Pola ini menunjukkan bahwa kinerja domestik yang kuat seringkali disertai dengan penerimaan internasional yang baik, menekankan pentingnya kedua pasar dalam kesuksesan finansial keseluruhan film.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 120px;'></p>", unsafe_allow_html=True)
    st.subheader("Runtime Distribution")
    st.markdown("""
                <div style='text-align: justify;'>
                 Box plot ini menggambarkan distribusi durasi film dan menunjukkan beberapa poin penting. Durasi film terendah adalah 1 jam, sementara durasi tertinggi adalah 3 jam. Kuartil pertama (Q1) menunjukkan bahwa 25% dari film memiliki durasi kurang dari atau sama dengan 1 jam. Nilai tengah atau median dari durasi film adalah 2 jam, yang berarti 50% dari film memiliki durasi kurang dari atau sama dengan 2 jam. Kuartil ketiga (Q3) mengindikasikan bahwa 75% dari film memiliki durasi kurang dari atau sama dengan 2 jam. Rentang antar kuartil (IQR) adalah 1 jam, menunjukkan bahwa variabilitas durasi film dalam kumpulan data ini tidak terlalu besar. Tidak ada pencilan (outliers) yang terdeteksi, menandakan bahwa durasi film cenderung konsisten tanpa nilai yang ekstrem.
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<p style='padding-top: 140px;'></p>", unsafe_allow_html=True)
    st.subheader("Top Movies by Gross Worldwide")
    st.markdown("""
                <div style='text-align: justify;'>
                 Pie chart ini menunjukkan distribusi warna dalam film. Sebagian besar film, yaitu 86,4%, dibuat dalam format berwarna, sementara sisanya 13,6% dibuat dalam format hitam-putih. Hal ini menandakan bahwa film berwarna jauh lebih dominan dibandingkan film hitam-putih dalam kumpulan data ini, mencerminkan preferensi industri film terhadap produksi film berwarna. Dominasi ini kemungkinan dipengaruhi oleh perkembangan teknologi dan preferensi audiens yang lebih memilih pengalaman visual yang lebih kaya dan beragam.
                </div>
                """, unsafe_allow_html=True)
