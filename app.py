import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt # Meskipun diimpor, tidak digunakan dalam kode yang ditampilkan
import numpy as np
import plotly.express as px
from joblib import load
import plotly.graph_objects as go

# Konfigurasi halaman dan Tema CSS Global
st.set_page_config(layout="wide")

# MODIFIKASI WARNA: CSS untuk tema gelap dasar
st.markdown("""
    <style>
    /* Target elemen utama Streamlit */
    .stApp {
        background-color: #1F2937; /* Latar belakang utama aplikasi (abu-abu sangat gelap kebiruan) */
        color: #EAEAEA; /* Warna teks default (putih keabuan) */
    }
    /* Sidebar styling */
    .st-emotion-cache-16txtl3 { /* Kelas umum untuk sidebar Streamlit (bisa berubah antar versi) */
        background-color: #2C3E50; /* Latar belakang sidebar (abu-abu gelap kebiruan lebih pekat) */
    }
    /* Styling untuk header */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF; /* Warna header (putih) */
    }
    /* Styling untuk subheader Streamlit (jika st.subheader digunakan) */
    .st-emotion-cache-1xarl3l {
        color: #BDC3C7; /* Warna subheader (abu-abu terang) */
    }
    /* Warna label widget */
    .stSelectbox label, .stNumberInput label, .stRadio label {
        color: #BDC3C7 !important; /* Abu-abu terang untuk label */
    }
    /* Tombol Streamlit umum */
    .stButton>button {
        border: 1px solid #3498DB; /* Border biru */
        background-color: #3498DB; /* Latar belakang biru */
        color: #FFFFFF; /* Teks putih */
        border-radius: 5px;
        padding: 0.4em 0.8em;
    }
    .stButton>button:hover {
        background-color: #2980B9; /* Biru lebih gelap saat hover */
        color: #FFFFFF;
        border: 1px solid #2980B9;
    }
    .stButton>button:active {
        background-color: #1F618D !important; /* Biru sangat gelap saat aktif */
        color: #FFFFFF !important;
        border: 1px solid #1F618D !important;
    }
    /* Border untuk st.container(border=True) */
    .st-emotion-cache-q8sbsg, .st-emotion-cache-4oy321 { /* Kelas untuk container border (bisa berubah) */
        border-color: #34495E !important; /* Warna border container (abu-abu gelap) */
        border-radius: 8px; /* Rounded corners untuk container */
    }
    /* Warna teks dari st.write default dan paragraf */
    p, .stMarkdown p {
        color: #BDC3C7; /* Abu-abu terang */
    }
    /* Warna link */
    a {
        color: #5DADE2; /* Biru muda untuk link */
    }
    a:hover {
        color: #85C1E9; /* Biru lebih terang saat hover */
    }

    /* Styling khusus untuk judul utama aplikasi */
    .st-emotion-cache- Sslotsk e1nzilvr5 > .st-emotion-cache-1dp5vir e1nzilvr4 > .st-emotion-cache- S192y4z e1nzilvr1 h1 {
         /* Ini sangat spesifik dan rapuh, jika judul Anda di dalam st.title() di luar container */
         color: #FFFFFF !important;
    }

    /* Custom styling untuk judul utama dashboard */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] > div.st-emotion-cache-1dp5vir > h1 {
        color: #FFFFFF !important; /* Putih untuk judul utama */
        text-align: center; /* tengahkan judul jika diinginkan */
        padding-bottom: 10px; /* sedikit padding bawah */
    }

    /* Styling untuk teks "Oleh: Bintang Budi Pangestu" */
     div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] > div.st-emotion-cache-1dp5vir > div[data-testid="stMarkdownContainer"] > p {
        text-align: center; /* tengahkan jika diinginkan */
        color: #BDC3C7; /* Warna abu-abu terang */
        font-style: italic; /* miringkan teks */
    }

    </style>
""", unsafe_allow_html=True)


data = pd.read_csv("databaru.csv", delimiter=",")
# Pastikan kolom Status_0, Status_1, Status_2, Status_New ada dan benar
# Jika Status_0, Status_1, Status_2 adalah hasil one-hot encoding dari Status,
# dan Status_New adalah (Status > 0).astype(int)
if 'Status_0' not in data.columns and 'Status' in data.columns:
    data['Status_0'] = (data['Status'] == 0).astype(int)
if 'Status_1' not in data.columns and 'Status' in data.columns:
    data['Status_1'] = (data['Status'] == 1).astype(int)
if 'Status_2' not in data.columns and 'Status' in data.columns:
    data['Status_2'] = (data['Status'] == 2).astype(int)
if 'Status_New' not in data.columns and 'Status' in data.columns:
     data['Status_New'] = (data['Status'] > 0).astype(int)


data_0 = data.loc[data['Status']==0]
data_1 = data.loc[data['Status']==1]
data_2 = data.loc[data['Status']==2]

category_mapping = {
    33: 'Biofuel Production Technologies', 171: 'Animation and Multimedia Design',
    8014: 'Social Service (evening attendance)', 9003: 'Agronomy',
    9070: 'Communication Design', 9085: 'Veterinary Nursing',
    9119: 'Informatics Engineering', 9130: 'Equinculture',
    9147: 'Management', 9238: 'Social Service', 9254: 'Tourism',
    9500: 'Nursing', 9556: 'Oral Hygiene',
    9670: 'Advertising and Marketing Management', 9773: 'Journalism and Communication',
    9853: 'Basic Education', 9991: 'Management (evening attendance)'
}
data['Course_Label'] = data['Course'].replace(category_mapping)

add_selectbox = st.sidebar.selectbox(
    "Choose a page",
    ("Dashboard", "Prediction")
)

# Warna dasar untuk grafik
PRIMARY_COLOR = "#3498DB" # Biru cerah
SECONDARY_COLOR = "#F39C12" # Oranye untuk highlight
BACKGROUND_COLOR_PLOT = "#2C3E50" # Abu-abu gelap kebiruan untuk latar plot
TEXT_COLOR_PLOT = "#EAEAEA" # Putih keabuan untuk teks plot
GRID_COLOR_PLOT = "#4A5A6A" # Abu-abu lebih lembut untuk grid
BAR_COLOR_NEUTRAL = "#7F8C8D" # Abu-abu netral untuk bar

def add_rating(content):
    return f"""
        <div style='
            height: auto;
            border: 1px solid {PRIMARY_COLOR};
            border-radius: 8px;
            font-size: 25px;
            padding: 38px 15px; /* Adjusted padding */
            background-color: {BACKGROUND_COLOR_PLOT};
            color: {TEXT_COLOR_PLOT};
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.3);
            word-wrap: break-word; /* Ensure text wraps */
            '>{content}</div>
        """

def add_card(content):
    return f"""
        <div style='
            height: auto;
            font-size: auto; /* Adjusted to auto, will inherit or be overridden by content */
            border: 1px solid {PRIMARY_COLOR};
            border-radius: 8px;
            padding: 15px; /* Adjusted padding */
            margin-bottom: 10px;
            background-color: {BACKGROUND_COLOR_PLOT};
            color: {TEXT_COLOR_PLOT};
            text-align: center;
            display: flex;
            flex-direction: column; /* Stack content vertically */
            justify-content: center;
            align-items: center;
            line-height: 1.5; /* Adjusted line height for better readability */
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.3);
            word-wrap: break-word; /* Ensure text wraps */
            min-height: 100px; /* Minimum height for consistency */
            '>{content}</div>
        """

def create_pie_chart(column, title):
    try:
        value_counts = kelas[column].value_counts()
        if value_counts.empty:
            st.write(f"No data available to display for {title}.")
            return

        names_map = {0: 'No', 1: 'Yes'} # Peta untuk legenda yang lebih jelas
        # Jika nama kolomnya adalah 'Educational_special_needs', 'Debtor', 'Tuition_fees_up_to_date'
        # Maka indexnya kemungkinan 0 dan 1.
        # Kita perlu memastikan 'names' sesuai dengan nilai yang ada di value_counts.index
        pie_names = [names_map.get(idx, idx) for idx in value_counts.index]

        # Warna: Biru untuk 'Yes' (1), Abu-abu Netral untuk 'No' (0)
        chart_colors_map = {'Yes': PRIMARY_COLOR, 'No': BAR_COLOR_NEUTRAL}
        final_colors = [chart_colors_map.get(name, BAR_COLOR_NEUTRAL) for name in pie_names]


        fig = px.pie(
            values=value_counts.values,
            names=pie_names,
            title=title,
            color_discrete_sequence=final_colors)
        fig.update_traces(textinfo='percent+label', marker=dict(line=dict(color=BACKGROUND_COLOR_PLOT, width=2)))
        fig.update_layout(
            height=250, # Sedikit lebih tinggi untuk pie chart
            margin=dict(l=10, r=10, t=70, b=20),
            title=dict(
                x=0.05, # Geser judul sedikit ke kanan dari tepi
                xanchor='left',
                font=dict(size=16, color=TEXT_COLOR_PLOT),
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=TEXT_COLOR_PLOT),
            legend_title_font_color=TEXT_COLOR_PLOT,
            legend_font_color=TEXT_COLOR_PLOT,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # Legenda di atas
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying pie chart for {title}: {e}")


if add_selectbox == "Dashboard":
    st.title('Jaya Jaya Institute Student Performance Dashboard')
    st.markdown("<p style='text-align:center; font-style:italic; color: #BDC3C7;'>Oleh: Bintang Budi Pangestu</p>", unsafe_allow_html=True)


    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    with col_filter1:
        status_options = ['None', 'Dropout', 'Not Dropout']
        selected_status_display = st.selectbox('Select status', status_options, key='initial_status_display')
        
        actual_selected_status = selected_status_display # Default
        if selected_status_display == 'Dropout':
            actual_selected_status = 0
        elif selected_status_display == 'Not Dropout':
            not_dropout_options = ['None', 'Enrolled', 'Graduated']
            selected_not_dropout_type = st.selectbox('Select type of Not Dropout', not_dropout_options, key='not_dropout_type')
            if selected_not_dropout_type == 'Enrolled':
                actual_selected_status = 1
            elif selected_not_dropout_type == 'Graduated':
                actual_selected_status = 2
            # Jika 'None' untuk sub-filter, maka kita filter untuk 'Not Dropout' secara umum
            # atau biarkan 'Not Dropout' yang berarti status 1 atau 2

    with col_filter2:
        course_list = ['None'] + sorted(list(data.Course_Label.unique()))
        selected_course = st.selectbox('Select course', course_list)

    with col_filter3:
        time_list = ['None', 'Daytime', 'Evening']
        selected_time_display = st.selectbox('Select attendance time', time_list)
        actual_selected_time = selected_time_display
        if selected_time_display == 'Daytime':
            actual_selected_time = 1
        elif selected_time_display == 'Evening':
            actual_selected_time = 0
            
    with col_filter4:
        gender_list = ['None', 'Male', 'Female']
        selected_gender_display = st.selectbox('Select gender', gender_list)
        actual_selected_gender = selected_gender_display
        if selected_gender_display == 'Male':
            actual_selected_gender = 1
        elif selected_gender_display == 'Female':
            actual_selected_gender = 0

    # Filtering logic
    kelas = data.copy()
    if selected_status_display == 'Dropout':
        kelas = kelas[kelas['Status'] == 0]
    elif selected_status_display == 'Not Dropout':
        if actual_selected_status in [1, 2]: # Enrolled atau Graduated
            kelas = kelas[kelas['Status'] == actual_selected_status]
        else: # 'None' dipilih untuk sub-filter, berarti semua Not Dropout (Status 1 atau 2)
            kelas = kelas[kelas['Status'].isin([1, 2])]
    # Jika selected_status_display == 'None', tidak ada filter status awal

    if selected_course != "None":
        kelas = kelas[kelas['Course_Label'] == selected_course]
    if actual_selected_time != "None":
        kelas = kelas[kelas['Daytime_evening_attendance'] == actual_selected_time]
    if actual_selected_gender != "None":
        kelas = kelas[kelas['Gender'] == actual_selected_gender]


    st.markdown("---") # Garis pemisah

    # KPI Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    with col_kpi1:
        total_students = len(kelas)
        st.markdown(add_card(f"<b>Total Students</b><br><span style='font-size: 32px; color:{PRIMARY_COLOR};'>{total_students}</span>"), unsafe_allow_html=True)

    if total_students > 0:
        dropout_count = kelas['Status_0'].sum()
        enrolled_count = kelas['Status_1'].sum()
        graduated_count = kelas['Status_2'].sum()

        dropout_rate_val = (dropout_count / total_students) * 100 if total_students > 0 else 0
        # enrolled_rate_val = (enrolled_count / total_students) * 100 if total_students > 0 else 0
        # graduation_rate_val = (graduated_count / total_students) * 100 if total_students > 0 else 0
        
        with col_kpi2:
            st.markdown(add_card(f"<b>Dropout Rate</b><br><span style='font-size: 32px; color:{SECONDARY_COLOR};'>{dropout_rate_val:.2f}%</span><br>({dropout_count} students)"), unsafe_allow_html=True)
        with col_kpi3:
            st.markdown(add_card(f"<b>Enrolled Students</b><br><span style='font-size: 32px; color:{PRIMARY_COLOR};'>{enrolled_count}</span>"), unsafe_allow_html=True)
        with col_kpi4:
            st.markdown(add_card(f"<b>Graduated Students</b><br><span style='font-size: 32px; color:lightgreen;'>{graduated_count}</span>"), unsafe_allow_html=True)
    else:
        for col_kpi in [col_kpi2, col_kpi3, col_kpi4]:
            with col_kpi:
                st.markdown(add_card("<b>N/A</b><br>No data for selection"), unsafe_allow_html=True)

    st.markdown("---")


    col_chart1, col_chart2 = st.columns(2)

    # Grouper logic
    # Grouper logic
    if selected_status_display == 'None':
        grouper = "Status" # Group by 0, 1, 2
        status_labels_map = {0: 'Dropout', 1: 'Enrolled', 2: 'Graduated'}
        kelas_chart = kelas # MODIFIED: Define kelas_chart here
    elif selected_status_display == 'Not Dropout' and actual_selected_status not in [1,2]: # 'None' untuk sub-filter Not Dropout
        grouper = "Status" # Group by 1, 2 (karena kelas sudah difilter untuk Status > 0)
        status_labels_map = {1: 'Enrolled', 2: 'Graduated'}
        # Pastikan kelas_chart hanya berisi status yang relevan untuk pengelompokan ini
        kelas_chart = kelas[kelas['Status'].isin([1,2])]
    elif actual_selected_status in [0,1,2]:
        # Jika status spesifik dipilih, tidak ada pengelompokan status lagi di chart
        grouper = None # Tidak ada grouper status, data sudah terfilter
        status_labels_map = {}
        kelas_chart = kelas # Data sudah terfilter
    else: # Fallback
        grouper = "Status"
        status_labels_map = {0: 'Dropout', 1: 'Enrolled', 2: 'Graduated'}
        kelas_chart = kelas # MODIFIED: Define kelas_chart here

    with col_chart1:
        st.subheader('Scholarship Holders by Status')
        if grouper and not kelas_chart.empty:
            scholarship_data = kelas_chart.groupby(grouper)['Scholarship_holder'].sum().reset_index()
            scholarship_data[grouper] = scholarship_data[grouper].map(status_labels_map).fillna('Unknown')
            
            if not scholarship_data.empty:
                max_val = scholarship_data['Scholarship_holder'].max()
                bar_colors = [SECONDARY_COLOR if val == max_val else PRIMARY_COLOR for val in scholarship_data['Scholarship_holder']]

                fig_scholarship = go.Figure(go.Bar(
                    x=scholarship_data[grouper],
                    y=scholarship_data['Scholarship_holder'],
                    text=scholarship_data['Scholarship_holder'],
                    textposition='auto',
                    marker_color=bar_colors
                ))
                fig_scholarship.update_layout(
                    xaxis_title='Status', yaxis_title='Number of Scholarship Holders',
                    plot_bgcolor=BACKGROUND_COLOR_PLOT, paper_bgcolor=BACKGROUND_COLOR_PLOT,
                    font_color=TEXT_COLOR_PLOT,
                    xaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    yaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    margin=dict(l=50, r=20, t=50, b=50)
                )
                st.plotly_chart(fig_scholarship, use_container_width=True)
            else:
                st.write("No scholarship data available for the current selection.")
        else:
            # Jika tidak ada grouper (status spesifik telah dipilih)
            if not kelas.empty:
                total_scholarship_holders = kelas['Scholarship_holder'].sum()
                st.markdown(f"<p style='font-size:18px; color:{TEXT_COLOR_PLOT};'>Total Scholarship Holders in this selection: <b style='color:{PRIMARY_COLOR};'>{total_scholarship_holders}</b></p>", unsafe_allow_html=True)
            else:
                st.write("No data to display for scholarship holders.")


    with col_chart2:
        st.subheader('Average Grade per Semester by Status')
        if grouper and not kelas_chart.empty:
            avg_grades = kelas_chart.groupby(grouper)[['Curricular_units_1st_sem_grade', 'Curricular_units_2nd_sem_grade']].mean().reset_index()
            avg_grades[grouper] = avg_grades[grouper].map(status_labels_map).fillna('Unknown')

            if not avg_grades.empty:
                fig_avg_grades = go.Figure()
                fig_avg_grades.add_trace(go.Bar(
                    x=avg_grades[grouper],
                    y=avg_grades['Curricular_units_1st_sem_grade'],
                    name='1st Sem Avg Grade',
                    marker_color=PRIMARY_COLOR,
                    text=[f"{val:.2f}" for val in avg_grades['Curricular_units_1st_sem_grade']], textposition='auto'
                ))
                fig_avg_grades.add_trace(go.Bar(
                    x=avg_grades[grouper],
                    y=avg_grades['Curricular_units_2nd_sem_grade'],
                    name='2nd Sem Avg Grade',
                    marker_color=SECONDARY_COLOR, # Gunakan warna lain untuk semester 2
                    text=[f"{val:.2f}" for val in avg_grades['Curricular_units_2nd_sem_grade']], textposition='auto'
                ))
                fig_avg_grades.update_layout(
                    barmode='group', xaxis_title='Status', yaxis_title='Average Grade',
                    plot_bgcolor=BACKGROUND_COLOR_PLOT, paper_bgcolor=BACKGROUND_COLOR_PLOT,
                    font_color=TEXT_COLOR_PLOT, legend_font_color=TEXT_COLOR_PLOT,
                    xaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    yaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    margin=dict(l=50, r=20, t=50, b=50),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_avg_grades, use_container_width=True)
            else:
                st.write("No average grade data available for the current selection.")
        else:
            if not kelas.empty:
                avg_1st_sem = kelas['Curricular_units_1st_sem_grade'].mean()
                avg_2nd_sem = kelas['Curricular_units_2nd_sem_grade'].mean()
                st.markdown(f"""
                <p style='font-size:18px; color:{TEXT_COLOR_PLOT};'>
                Average 1st Semester Grade: <b style='color:{PRIMARY_COLOR};'>{avg_1st_sem:.2f}</b><br>
                Average 2nd Semester Grade: <b style='color:{SECONDARY_COLOR};'>{avg_2nd_sem:.2f}</b>
                </p>
                """, unsafe_allow_html=True)
            else:
                st.write("No data to display for average grades.")

    st.markdown("---")

    # Dropout Rate by Course and Pie Charts in one container with columns
    container_course_pies = st.container(border=True)
    with container_course_pies:
        col_course_bar, col_pies = st.columns([3, 2]) # Beri lebih banyak ruang untuk bar chart

        with col_course_bar:
            st.subheader("Dropout Rate by Course (%)")
            if not kelas.empty:
                # Hitung dropout (Status_0 == 1) dan non-dropout (Status_0 == 0) per kursus
                # Pastikan Status_0 adalah 1 untuk dropout, 0 untuk tidak dropout
                course_dropout_counts = kelas[kelas['Status_0'] == 1].groupby('Course_Label').size()
                course_total_counts = kelas.groupby('Course_Label').size()
                
                # Hindari pembagian dengan nol jika course_total_counts memiliki nol untuk beberapa kursus
                dropout_rate_by_course = (course_dropout_counts.reindex(course_total_counts.index, fill_value=0) / course_total_counts.replace(0, np.nan) * 100).fillna(0).sort_values()
                
                if not dropout_rate_by_course.empty:
                    max_rate_course = dropout_rate_by_course.idxmax() if not dropout_rate_by_course.empty else None
                    bar_colors_course = [SECONDARY_COLOR if course == max_rate_course else PRIMARY_COLOR for course in dropout_rate_by_course.index]

                    fig_course_dropout = px.bar(
                        x=dropout_rate_by_course.values,
                        y=dropout_rate_by_course.index,
                        orientation='h',
                        labels={'y': 'Course', 'x': 'Dropout Rate (%)'},
                        text=[f"{val:.1f}%" for val in dropout_rate_by_course.values],
                        color=dropout_rate_by_course.index, # Untuk legenda otomatis
                        color_discrete_sequence=px.colors.qualitative.Plotly # Palet warna yang beragam
                    )
                    # Untuk highlight:
                    # fig_course_dropout.update_traces(marker_color=bar_colors_course) # Ini akan menimpa color_discrete_sequence

                    fig_course_dropout.update_traces(textposition='outside')
                    fig_course_dropout.update_layout(
                        height=max(400, len(dropout_rate_by_course) * 30), # Tinggi dinamis
                        plot_bgcolor=BACKGROUND_COLOR_PLOT, paper_bgcolor=BACKGROUND_COLOR_PLOT,
                        font_color=TEXT_COLOR_PLOT,
                        xaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                        yaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT, autorange="reversed"), # agar rate tertinggi di atas
                        margin=dict(l=50, r=20, t=50, b=50),
                        showlegend=False # Terlalu banyak legend bisa jadi crowded
                    )
                    st.plotly_chart(fig_course_dropout, use_container_width=True)
                else:
                    st.write("No dropout rate data by course for the current selection.")
            else:
                st.write("No data for course dropout rates.")

        with col_pies:
            if not kelas.empty:
                st.subheader("Student Characteristics")
                create_pie_chart('Educational_special_needs', 'Special Needs')
                create_pie_chart('Debtor', 'Debtor Status')
                create_pie_chart('Tuition_fees_up_to_date', 'Tuition Fees Paid')
            else:
                st.write("No data for student characteristics pies.")
                
    st.markdown("---")

    # Age Distribution
    container_age = st.container(border=True)
    with container_age:
        col_hist, col_age_kpi = st.columns([3,1])
        with col_hist:
            st.subheader('Age at Enrollment Distribution')
            if not kelas.empty and 'Age_at_enrollment' in kelas.columns:
                fig_age_hist = px.histogram(
                    kelas, x='Age_at_enrollment', nbins=20, # Sesuaikan nbins jika perlu
                    color_discrete_sequence=[PRIMARY_COLOR]
                )
                fig_age_hist.update_layout(
                    bargap=0.1,
                    plot_bgcolor=BACKGROUND_COLOR_PLOT, paper_bgcolor=BACKGROUND_COLOR_PLOT,
                    font_color=TEXT_COLOR_PLOT,
                    xaxis_title='Age at Enrollment', yaxis_title='Number of Students',
                    xaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    yaxis=dict(gridcolor=GRID_COLOR_PLOT, linecolor=GRID_COLOR_PLOT),
                    margin=dict(l=50, r=20, t=50, b=50)
                )
                st.plotly_chart(fig_age_hist, use_container_width=True)
            else:
                st.write("No age data available.")

        with col_age_kpi:
            st.subheader("Age Stats")
            if not kelas.empty and 'Age_at_enrollment' in kelas.columns:
                max_age = int(kelas['Age_at_enrollment'].max())
                mean_age = round(kelas['Age_at_enrollment'].mean(), 1)
                min_age = int(kelas['Age_at_enrollment'].min())
                st.markdown(add_card(f"<b>Min Age</b><br><span style='font-size: 28px; color:{PRIMARY_COLOR};'>{min_age}</span>"), unsafe_allow_html=True)
                st.markdown(add_card(f"<b>Avg Age</b><br><span style='font-size: 28px; color:{PRIMARY_COLOR};'>{mean_age}</span>"), unsafe_allow_html=True)
                st.markdown(add_card(f"<b>Max Age</b><br><span style='font-size: 28px; color:{PRIMARY_COLOR};'>{max_age}</span>"), unsafe_allow_html=True)
            else:
                st.markdown(add_card("<b>N/A</b>"), unsafe_allow_html=True)
                st.markdown(add_card("<b>N/A</b>"), unsafe_allow_html=True)
                st.markdown(add_card("<b>N/A</b>"), unsafe_allow_html=True)

elif add_selectbox == "Prediction":
    st.subheader("Student Dropout Likelihood Prediction")
    st.markdown("<p style='color:#BDC3C7;'>Enter the student's details below to predict their likelihood of dropping out.</p>", unsafe_allow_html=True)

    course_list_pred = sorted(list(data.Course_Label.unique())) # Tidak perlu 'None' di sini

    if 'pred_selected_course' not in st.session_state:
        st.session_state.pred_selected_course = course_list_pred[0] # Default ke item pertama

    # Input Fields dalam dua kolom untuk kerapian
    col_pred1, col_pred2 = st.columns(2)

    with col_pred1:
        course_selected_label = st.selectbox('Course', course_list_pred, key='pred_course_label')
        reverse_mapping = {v: k for k, v in category_mapping.items()}
        course_selected_code = reverse_mapping.get(course_selected_label, 0) # Default ke 0 jika tidak ketemu

        admgrade_selected = st.number_input("Admission Grade (0-200)", value=120.0, step=0.1, min_value=0.0, max_value=200.0, format="%.1f")
        
        gender_options = {'Male': 1, 'Female': 0}
        gender_selected_label = st.selectbox('Gender', list(gender_options.keys()))
        gender_selected_code = gender_options[gender_selected_label]

        special_options = {'No': 0, 'Yes': 1}
        special_selected_label = st.radio('Special Education Needs?', list(special_options.keys()), horizontal=True)
        special_selected_code = special_options[special_selected_label]

        debtor_options = {'No': 0, 'Yes': 1}
        debtor_selected_label = st.radio('Debtor?', list(debtor_options.keys()), horizontal=True)
        debtor_selected_code = debtor_options[debtor_selected_label]


    with col_pred2:
        # Daytime/evening attendance (otomatis berdasarkan course, tapi bisa juga manual jika model membutuhkannya sbg input eksplisit)
        if course_selected_code in [9991, 8014]: # Evening courses
            time_selected_code = 0
            st.info("Attendance time set to 'Evening' based on selected course.")
        else: # Daytime courses
            time_selected_code = 1
            st.info("Attendance time set to 'Daytime' based on selected course.")

        age_selected = st.number_input("Age at Enrollment (17-70)", value=18, step=1, min_value=17, max_value=70)
        
        tuition_options = {'Yes (Up to date)': 1, 'No (Not up to date)': 0}
        tuition_selected_label = st.radio('Tuition Fees Up to Date?', list(tuition_options.keys()), horizontal=True)
        tuition_selected_code = tuition_options[tuition_selected_label]

        scholarship_options = {'No': 0, 'Yes': 1}
        scholarship_selected_label = st.radio('Scholarship Holder?', list(scholarship_options.keys()), horizontal=True)
        scholarship_selected_code = scholarship_options[scholarship_selected_label]

        grade1_selected = st.number_input("1st Semester Approved Units Grade (0-20)", value=10.0, step=0.1, min_value=0.0, max_value=20.0, format="%.2f")
        grade2_selected = st.number_input("2nd Semester Approved Units Grade (0-20)", value=10.0, step=0.1, min_value=0.0, max_value=20.0, format="%.2f")
    
    st.markdown("---")
    
    # Tombol Predict di tengah
    col_btn_empty1, col_btn, col_btn_empty2 = st.columns([2,1,2])
    with col_btn:
        button_predict = st.button("✨ Predict Likelihood", key='predict_button', use_container_width=True)

    if button_predict:
        try:
            model = load('model.joblib')
            user_data = {
                'Course': [course_selected_code],
                'Daytime_evening_attendance': [time_selected_code],
                'Admission_grade': [round(admgrade_selected,1)],
                'Educational_special_needs': [special_selected_code],
                'Debtor': [debtor_selected_code],
                'Tuition_fees_up_to_date': [tuition_selected_code],
                'Gender': [gender_selected_code],
                'Scholarship_holder': [scholarship_selected_code],
                'Age_at_enrollment': [age_selected],
                'Curricular_units_1st_sem_grade': [round(grade1_selected,2)],
                'Curricular_units_2nd_sem_grade': [round(grade2_selected,2)]
            }

            # Pastikan urutan kolom sesuai dengan yang diharapkan model
            # Jika model Anda dilatih dengan urutan kolom tertentu, X_new harus memiliki urutan itu
            expected_columns = ['Course', 'Daytime_evening_attendance', 'Admission_grade', 
                                'Educational_special_needs', 'Debtor', 'Tuition_fees_up_to_date', 
                                'Gender', 'Scholarship_holder', 'Age_at_enrollment', 
                                'Curricular_units_1st_sem_grade', 'Curricular_units_2nd_sem_grade']
            X_new = pd.DataFrame(user_data, columns=expected_columns)

            predictions = model.predict(X_new)
            prediction_proba = model.predict_proba(X_new) # Probabilitas

            st.subheader("Prediction Result")
            # proba_dropout = prediction_proba[0][0] * 100 # Asumsi kelas 0 adalah Dropout
            # proba_not_dropout = prediction_proba[0][1] * 100 # Asumsi kelas 1 adalah Not Dropout

            # Cari tahu kelas mana yang dropout (biasanya 0) dari model.classes_
            # Misal model.classes_ adalah [0, 1] dimana 0 = Dropout, 1 = Not Dropout
            idx_dropout = np.where(model.classes_ == 0)[0][0] if 0 in model.classes_ else None
            idx_not_dropout = np.where(model.classes_ == 1)[0][0] if 1 in model.classes_ else None


            if predictions[0] == 0: # Asumsi 0 adalah Dropout
                proba_val = prediction_proba[0][idx_dropout] * 100 if idx_dropout is not None else 50 # Default jika tidak ketemu
                st.error(f"🚨 Student is LIKELY to **Dropout** (Confidence: {proba_val:.2f}%)")
                st.progress(int(proba_val))
                st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbzM4ZThjNm92c2ZyZWR0bTJlNWM0d2M5bWN2dzNtd2hyYjJwdDNzYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7btPYt2u55XJVxAI/giphy.gif", width=200) # Contoh GIF
            elif predictions[0] == 1 or predictions[0] == 2: # Asumsi 1 atau 2 adalah Not Dropout (Enrolled/Graduated)
                proba_val = prediction_proba[0][idx_not_dropout] * 100 if idx_not_dropout is not None else 50
                st.success(f"✅ Student is LIKELY to **Continue (Not Dropout)** (Confidence: {proba_val:.2f}%)")
                st.progress(int(proba_val)) # Menunjukkan probabilitas untuk kelas yang diprediksi
                st.image("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2Jhd3FjMnN2bzhsY216enI0MnZ0b2lmbzVqZnRtcjM4dDdqMTZtNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3oz8xAFtqoOUUrsh7W/giphy.gif", width=200)
            else: # Fallback jika prediksi bukan 0, 1, atau 2
                 st.warning(f"Prediction outcome: {predictions[0]}. Please check model output interpretation.")


        except FileNotFoundError:
            st.error("Model file 'model.joblib' not found. Please ensure the model is in the correct path.")
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")