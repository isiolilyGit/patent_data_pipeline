import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# ─────────────────────────────────────────────
# LOAD ENVIRONMENT VARIABLES
# ─────────────────────────────────────────────

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Patent Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .stMetric {
        background-color: #111827;
        padding: 15px;
        border-radius: 12px;
    }

    .css-1d391kg {
        background-color: #111827;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────────────

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

st.sidebar.title("📂 Navigation")

page = st.sidebar.radio(
    "Go To",
    [
        "Overview",
        "Companies",
        "Inventors",
        "Countries",
        "Technology Trends",
        "Network Analysis",
        "Data Explorer"
    ]
)

st.sidebar.markdown("---")

st.sidebar.header("Dashboard Filters")

# YEARS

years_query = """
SELECT DISTINCT year
FROM patents
WHERE year IS NOT NULL
ORDER BY year;
"""

years_df = pd.read_sql(years_query, engine)

min_year = int(years_df["year"].min())
max_year = int(years_df["year"].max())

selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# TOP N

top_n = st.sidebar.selectbox(
    "Top Results",
    [5, 10, 20, 50],
    index=1
)

# SORT ORDER

sort_order = st.sidebar.radio(
    "Sort Order",
    ["Descending", "Ascending"]
)

ascending = sort_order == "Ascending"

# CHART TYPE

chart_type = st.sidebar.selectbox(
    "Chart Type",
    ["Bar", "Line", "Area"]
)

# SEARCH

search_text = st.sidebar.text_input(
    "Search Patent Titles"
)

# CATEGORY FILTER

selected_categories = st.sidebar.multiselect(
    "Technology Categories",
    [
        "AI",
        "Biotech",
        "Energy",
        "Medical",
        "Telecommunications",
        "Automotive"
    ],
    default=["AI", "Energy"]
)

# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────

st.title("📊 Patent Analytics Dashboard")

st.markdown(
    """
    Interactive analytics platform for patent data analysis using:
    - PostgreSQL
    - pandas
    - SQL
    - Streamlit
    - Plotly
    """
)

# ─────────────────────────────────────────────
# YEAR FILTER
# ─────────────────────────────────────────────

year_filter = f"""
WHERE year BETWEEN {selected_years[0]}
AND {selected_years[1]}
"""

# ─────────────────────────────────────────────
# OVERVIEW PAGE
# ─────────────────────────────────────────────

if page == "Overview":

    st.header("📈 Dashboard Overview")

    # KPIs

    kpi_query = f"""
    SELECT
        COUNT(*) AS total_patents,
        COUNT(DISTINCT year) AS total_years
    FROM patents
    {year_filter};
    """

    kpi_df = pd.read_sql(kpi_query, engine)

    inventor_query = """
    SELECT COUNT(DISTINCT inventor_id)
    AS total_inventors
    FROM inventors;
    """

    company_query = """
    SELECT COUNT(DISTINCT company_id)
    AS total_companies
    FROM companies;
    """

    inventor_df = pd.read_sql(inventor_query, engine)
    company_df = pd.read_sql(company_query, engine)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Patents",
        f"{kpi_df['total_patents'][0]:,}"
    )

    col2.metric(
        "Total Inventors",
        f"{inventor_df['total_inventors'][0]:,}"
    )

    col3.metric(
        "Total Companies",
        f"{company_df['total_companies'][0]:,}"
    )

    col4.metric(
        "Years Covered",
        f"{kpi_df['total_years'][0]}"
    )

    st.markdown("---")

    # PATENT TRENDS

    query = f"""
    SELECT
        year,
        COUNT(*) AS patents_per_year

    FROM patents

    {year_filter}

    GROUP BY year
    ORDER BY year;
    """

    df = pd.read_sql(query, engine)

    if chart_type == "Bar":
        fig = px.bar(
            df,
            x="year",
            y="patents_per_year",
            title="Patent Trends Over Time"
        )

    elif chart_type == "Area":
        fig = px.area(
            df,
            x="year",
            y="patents_per_year",
            title="Patent Trends Over Time"
        )

    else:
        fig = px.line(
            df,
            x="year",
            y="patents_per_year",
            markers=True,
            title="Patent Trends Over Time"
        )

    st.plotly_chart(fig, use_container_width=True)

    # DOWNLOAD BUTTON

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Trend Data",
        csv,
        "patent_trends.csv",
        "text/csv"
    )

# ─────────────────────────────────────────────
# COMPANIES PAGE
# ─────────────────────────────────────────────

elif page == "Companies":

    st.header("🏢 Top Companies")

    query = f"""
    SELECT
        c.name,
        COUNT(pr.patent_id) AS patent_count

    FROM companies c

    JOIN patent_relationships pr
        ON c.company_id = pr.company_id

    JOIN patents p
        ON pr.patent_id = p.patent_id

    WHERE p.year BETWEEN {selected_years[0]}
    AND {selected_years[1]}

    GROUP BY c.name

    ORDER BY patent_count
    {"ASC" if ascending else "DESC"}

    LIMIT {top_n};
    """

    df = pd.read_sql(query, engine)

    fig = px.bar(
        df,
        x="name",
        y="patent_count",
        title="Top Patent Owning Companies"
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View SQL Query"):

        st.code(query, language="sql")

# ─────────────────────────────────────────────
# INVENTORS PAGE
# ─────────────────────────────────────────────

elif page == "Inventors":

    st.header("👨‍🔬 Top Inventors")

    query = f"""
    SELECT
        i.name,
        COUNT(pr.patent_id) AS patent_count

    FROM inventors i

    JOIN patent_relationships pr
        ON i.inventor_id = pr.inventor_id

    JOIN patents p
        ON pr.patent_id = p.patent_id

    WHERE p.year BETWEEN {selected_years[0]}
    AND {selected_years[1]}

    GROUP BY i.name

    ORDER BY patent_count
    {"ASC" if ascending else "DESC"}

    LIMIT {top_n};
    """

    df = pd.read_sql(query, engine)

    fig = px.bar(
        df,
        x="name",
        y="patent_count",
        title="Top Inventors"
    )

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# COUNTRIES PAGE
# ─────────────────────────────────────────────

elif page == "Countries":

    st.header("🌍 Patent Distribution by Country")

    query = """
    SELECT
        country,
        COUNT(*) AS patent_count

    FROM inventors

    WHERE country IS NOT NULL

    GROUP BY country

    ORDER BY patent_count DESC

    LIMIT 15;
    """

    df = pd.read_sql(query, engine)

    fig = px.pie(
        df,
        names="country",
        values="patent_count",
        title="Patent Distribution by Country"
    )

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# TECHNOLOGY TRENDS PAGE
# ─────────────────────────────────────────────

elif page == "Technology Trends":

    st.header("⚙ Technology Category Analysis")

    query = """
    SELECT
        patent_id,
        title,
        year
    FROM patents
    WHERE title IS NOT NULL;
    """

    patents_df = pd.read_sql(query, engine)

    categories = {
        "AI": [
            "machine learning",
            "artificial intelligence",
            "neural network",
            "deep learning",
        ],

        "Biotech": [
            "gene",
            "protein",
            "dna",
            "biological",
        ],

        "Energy": [
            "battery",
            "solar",
            "electric",
            "energy",
        ],

        "Telecommunications": [
            "wireless",
            "network",
            "signal",
            "communication",
        ],

        "Medical": [
            "medical",
            "surgical",
            "treatment",
            "health",
        ],

        "Automotive": [
            "vehicle",
            "engine",
            "automobile",
            "driving",
        ]
    }

    patents_df["category"] = "Other"

    for category, keywords in categories.items():

        mask = patents_df["title"].str.lower().str.contains(
            "|".join(keywords),
            na=False
        )

        patents_df.loc[mask, "category"] = category

    patents_df = patents_df[
        patents_df["category"].isin(selected_categories)
    ]

    summary = (
        patents_df["category"]
        .value_counts()
        .reset_index()
    )

    summary.columns = ["category", "count"]

    fig = px.bar(
        summary,
        x="category",
        y="count",
        title="Technology Categories"
    )

    st.plotly_chart(fig, use_container_width=True)

    # YEARLY TRENDS

    trend_summary = (
        patents_df.groupby(
            ["year", "category"]
        )
        .size()
        .reset_index(name="count")
    )

    fig = px.line(
        trend_summary,
        x="year",
        y="count",
        color="category",
        title="Technology Evolution Trends"
    )

    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# NETWORK ANALYSIS PAGE
# ─────────────────────────────────────────────

elif page == "Network Analysis":

    st.header("🕸 Inventor-Company Collaboration Network")

    query = """
    SELECT
        i.name AS inventor,
        c.name AS company

    FROM patent_relationships pr

    JOIN inventors i
        ON pr.inventor_id = i.inventor_id

    JOIN companies c
        ON pr.company_id = c.company_id

    LIMIT 50;
    """

    df = pd.read_sql(query, engine)

    G = nx.Graph()

    for _, row in df.iterrows():

        G.add_edge(
            row["inventor"],
            row["company"]
        )

    fig, ax = plt.subplots(figsize=(12, 8))

    nx.draw(
        G,
        with_labels=True,
        node_size=500,
        font_size=8,
        ax=ax
    )

    st.pyplot(fig)

# ─────────────────────────────────────────────
# DATA EXPLORER PAGE
# ─────────────────────────────────────────────

elif page == "Data Explorer":

    st.header("🔎 Patent Data Explorer")

    query = f"""
    SELECT
        patent_id,
        title,
        filing_date,
        year

    FROM patents

    WHERE year BETWEEN {selected_years[0]}
    AND {selected_years[1]}

    LIMIT 1000;
    """

    df = pd.read_sql(query, engine)

    if search_text:

        df = df[
            df["title"]
            .str.contains(search_text,
                          case=False,
                          na=False)
        ]

    st.dataframe(
        df,
        use_container_width=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download Explorer Data",
        csv,
        "patent_explorer.csv",
        "text/csv"
    )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown("---")

st.markdown(
    """
    ### 🛠 Technologies Used

    - Python
    - pandas
    - PostgreSQL
    - SQLAlchemy
    - Streamlit
    - Plotly
    - NetworkX
    - Matplotlib

    ---
    Patent Analytics Pipeline Project
    """
)