import base64
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="CWTS Leiden Ranking 2026",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "ranking_2026.parquet"
LOGO_PATH = ROOT / "assets" / "vyshe_kvartilei_avatar.jpg"
FLAG_DIR = ROOT / "assets" / "flags"
LATEST_START = 2021

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1500px;}
      h1, h2, h3 {letter-spacing: -0.025em;}
      h2 {border-left: 4px solid #3f82c8; padding-left: .65rem;}
      .brand-attribution {background: color-mix(in srgb, var(--primary-color, #3f82c8) 10%, var(--background-color, #ffffff));
        border: 1px solid color-mix(in srgb, var(--primary-color, #3f82c8) 34%, var(--background-color, #ffffff));
        border-radius: .75rem; color: var(--text-color, #182230);
        padding: .65rem .9rem; font-size: .92rem; margin: .2rem 0 1rem;}
      .brand-header {display: flex; align-items: center; gap: 1rem; margin-top: .45rem; margin-bottom: .35rem;}
      .brand-header img {width: 72px; height: 72px; object-fit: cover; border-radius: .65rem; flex: 0 0 72px;}
      .brand-header h1 {font-size: 2.65rem; line-height: 1.05; margin: 0 0 .4rem; font-weight: 700;}
      .brand-header .hero-note {color: inherit; opacity: .9; font-size: 1.02rem; margin: 0;}
      .brand-attribution a {color: inherit; font-weight: 700; text-decoration: underline; text-underline-offset: .12em;}
      .country-badges {display: flex; flex-wrap: wrap; gap: .4rem; margin: .25rem 0 .55rem;}
      .country-badge {display: inline-flex; align-items: center; gap: .4rem; padding: .25rem .55rem;
        border-radius: 999px; border: 1px solid #9eacbd;
        background: #f3f6fb; color: #182230 !important; font-size: .9rem;}
      .country-badge span {color: #182230 !important;}
      .country-badge img {width: 22px; height: 16px; object-fit: cover; border-radius: 2px;
        box-shadow: 0 0 0 1px color-mix(in srgb, var(--text-color, #182230) 14%, transparent);}
      [data-testid="stMetric"] {min-width: 0; overflow: hidden;
        background: #f3f6fb; border: 1px solid #aab8c9;
        color: #182230; padding: 0.8rem .9rem; border-radius: 0.7rem;}
      [data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stMetricDelta"] {
        color: #182230 !important; opacity: 1 !important; max-width: 100%;}
      [data-testid="stMetricLabel"] {font-size: clamp(.68rem, .8vw, .86rem) !important;
        line-height: 1.24 !important; white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stMetricLabel"] > div {white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stMetricValue"] {min-width: 0; font-size: clamp(1rem, 1.55vw, 1.55rem) !important;
        line-height: 1.12 !important; white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stMetricValue"] > div {white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stMetricDelta"] {font-size: clamp(.68rem, .78vw, .82rem) !important;
        line-height: 1.25 !important; white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stMetricDelta"] > div {white-space: normal !important; overflow-wrap: anywhere;}
      [data-testid="stVerticalBlockBorderWrapper"] {min-width: 0;}
      .hero-note {color: inherit; opacity: .9; font-size: 1.02rem; margin-top: -0.35rem;}
      .source-note {color: var(--text-color, #69778c); opacity: 1; font-size: 0.88rem;}
      @media (max-width: 700px) {
        .brand-header {align-items: flex-start; gap: .7rem;}
        .brand-header img {width: 58px; height: 58px; flex-basis: 58px;}
        .brand-header h1 {font-size: clamp(1.5rem, 6vw, 2.2rem);}
        [data-testid="stMetric"] {padding: .65rem .7rem;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


METRICS = {
    "Научное влияние": {
        "Публикации — P": "P",
        "Доля публикаций в top 1% по цитируемости": "PP_top_1",
        "Доля публикаций в top 5% по цитируемости": "PP_top_5",
        "Доля публикаций в top 10% по цитируемости": "PP_top_10",
        "Доля публикаций в top 50% по цитируемости": "PP_top_50",
        "Число публикаций в top 1%": "P_top_1",
        "Число публикаций в top 5%": "P_top_5",
        "Число публикаций в top 10%": "P_top_10",
        "Число публикаций в top 50%": "P_top_50",
        "Среднее нормализованное число цитирований — MNCS": "MNCS",
        "Среднее число цитирований — MCS": "MCS",
        "Всего нормализованных цитирований — TNCS": "TNCS",
        "Всего цитирований — TCS": "TCS",
    },
    "Сотрудничество": {
        "Публикации с соавторами из других организаций — число": "P_collab",
        "Публикации с соавторами из других организаций": "PP_collab",
        "Международное соавторство — число": "P_int_collab",
        "Международное соавторство": "PP_int_collab",
        "Сотрудничество с индустрией — число": "P_industry_collab",
        "Сотрудничество с индустрией": "PP_industry_collab",
        "Сотрудничество на расстоянии менее 100 км — число": "P_short_dist_collab",
        "Сотрудничество на расстоянии менее 100 км": "PP_short_dist_collab",
        "Сотрудничество на расстоянии более 5000 км — число": "P_long_dist_collab",
        "Сотрудничество на расстоянии более 5000 км": "PP_long_dist_collab",
    },
    "Открытый доступ": {
        "Все публикации открытого доступа — число": "P_OA",
        "Все публикации открытого доступа": "PP_OA",
        "Gold OA — число": "P_gold_OA",
        "Gold OA": "PP_gold_OA",
        "Hybrid OA — число": "P_hybrid_OA",
        "Hybrid OA": "PP_hybrid_OA",
        "Bronze OA — число": "P_bronze_OA",
        "Bronze OA": "PP_bronze_OA",
        "Green OA — число": "P_green_OA",
        "Green OA": "PP_green_OA",
        "Публикации с неизвестным статусом OA — число": "P_OA_unknown",
        "Статус OA неизвестен": "PP_OA_unknown",
    },
    "Гендер": {
        "Все авторства — число": "A",
        "Авторства с определённым гендером — число": "A_MF",
        "Авторства с неизвестным гендером — число": "A_gender_unknown",
        "Мужские авторства — число": "A_M",
        "Женские авторства — число": "A_F",
        "Женские авторства среди авторств с известным гендером": "PA_F_MF",
        "Мужские авторства среди авторств с известным гендером": "PA_M_MF",
        "Женские авторства среди всех авторств": "PA_F",
        "Мужские авторства среди всех авторств": "PA_M",
        "Авторства с неизвестным гендером": "PA_gender_unknown",
    },
}

RATE_META = {
    "PP_top_1": ("P_top_1", "P"),
    "PP_top_5": ("P_top_5", "P"),
    "PP_top_10": ("P_top_10", "P"),
    "PP_top_50": ("P_top_50", "P"),
    "PP_collab": ("P_collab", "P"),
    "PP_int_collab": ("P_int_collab", "P"),
    "PP_industry_collab": ("P_industry_collab", "P"),
    "PP_short_dist_collab": ("P_short_dist_collab", "P"),
    "PP_long_dist_collab": ("P_long_dist_collab", "P"),
    "PP_OA": ("P_OA", "P"),
    "PP_gold_OA": ("P_gold_OA", "P"),
    "PP_hybrid_OA": ("P_hybrid_OA", "P"),
    "PP_bronze_OA": ("P_bronze_OA", "P"),
    "PP_green_OA": ("P_green_OA", "P"),
    "PP_OA_unknown": ("P_OA_unknown", "P"),
    "PA_F_MF": ("A_F", "A_MF"),
    "PA_M_MF": ("A_M", "A_MF"),
    "PA_F": ("A_F", "A"),
    "PA_M": ("A_M", "A"),
    "PA_gender_unknown": ("A_gender_unknown", "A"),
}

AVERAGE_META = {
    "MNCS": ("TNCS", "P"),
    "MCS": ("TCS", "P"),
}

CI_META = {
    "PP_top_1": ("PP_top_1_lb", "PP_top_1_ub"),
    "PP_top_5": ("PP_top_5_lb", "PP_top_5_ub"),
    "PP_top_10": ("PP_top_10_lb", "PP_top_10_ub"),
    "PP_top_50": ("PP_top_50_lb", "PP_top_50_ub"),
    "PP_collab": ("PP_collab_lb", "PP_collab_ub"),
    "PP_int_collab": ("PP_int_collab_lb", "PP_int_collab_ub"),
    "PP_industry_collab": ("PP_industry_collab_lb", "PP_industry_collab_ub"),
    "PP_short_dist_collab": ("PP_short_dist_collab_lb", "PP_short_dist_collab_ub"),
    "PP_long_dist_collab": ("PP_long_dist_collab_lb", "PP_long_dist_collab_ub"),
    "PP_OA": ("PP_OA_lb", "PP_OA_ub"),
    "PP_gold_OA": ("PP_gold_OA_lb", "PP_gold_OA_ub"),
    "PP_hybrid_OA": ("PP_hybrid_OA_lb", "PP_hybrid_OA_ub"),
    "PP_bronze_OA": ("PP_bronze_OA_lb", "PP_bronze_OA_ub"),
    "PP_green_OA": ("PP_green_OA_lb", "PP_green_OA_ub"),
    "PP_OA_unknown": ("PP_OA_unknown_lb", "PP_OA_unknown_ub"),
    "MNCS": ("MNCS_lb", "MNCS_ub"),
    "MCS": ("MCS_lb", "MCS_ub"),
}

FIELD_ORDER = [
    "All sciences",
    "Biomedical and health sciences",
    "Life and earth sciences",
    "Mathematics and computer science",
    "Physical sciences and engineering",
    "Social sciences and humanities",
]

FIELD_RU = {
    "All sciences": "Все науки",
    "Biomedical and health sciences": "Биомедицинские и медицинские науки",
    "Life and earth sciences": "Науки о жизни и Земле",
    "Mathematics and computer science": "Математика и компьютерные науки",
    "Physical sciences and engineering": "Физические науки и инженерия",
    "Social sciences and humanities": "Общественные и гуманитарные науки",
}

UNIVERSITY_RU = {
    "HSE University": "НИУ ВШЭ",
    "IM Sechenov First Moscow State Medical University": "Сеченовский Университет",
    "ITMO University": "Университет ИТМО",
    "Kazan Federal University, Volga": "Казанский федеральный университет",
    "Lomonosov Moscow State University": "МГУ имени М. В. Ломоносова",
    "Moscow Institute of Physics and Technology": "МФТИ",
    "National Research Nuclear University MEPhI": "НИЯУ МИФИ",
    "National University of Science and Technology MISIS": "Университет МИСИС",
    "Novosibirsk State University": "Новосибирский государственный университет",
    "Peter the Great St. Petersburg Polytechnic University": "СПбПУ Петра Великого",
    "RUDN University": "РУДН",
    "Saint Petersburg State University": "Санкт-Петербургский государственный университет",
    "Skolkovo Institute of Science and Technology": "Сколковский институт науки и технологий",
    "Southern Federal University": "Южный федеральный университет",
    "Tomsk Polytechnic University": "Томский политехнический университет",
    "Tomsk State University": "Томский государственный университет",
    "Ural Federal University": "Уральский федеральный университет",
}

COUNTRY_RU = {
    "Algeria": "Алжир",
    "Argentina": "Аргентина",
    "Australia": "Австралия",
    "Austria": "Австрия",
    "Bangladesh": "Бангладеш",
    "Belgium": "Бельгия",
    "Brazil": "Бразилия",
    "Cameroon": "Камерун",
    "Canada": "Канада",
    "Chile": "Чили",
    "China": "Китай",
    "Colombia": "Колумбия",
    "Croatia": "Хорватия",
    "Cyprus": "Кипр",
    "Czechia": "Чехия",
    "Denmark": "Дания",
    "Egypt": "Египет",
    "Estonia": "Эстония",
    "Ethiopia": "Эфиопия",
    "Finland": "Финляндия",
    "France": "Франция",
    "Germany": "Германия",
    "Ghana": "Гана",
    "Greece": "Греция",
    "Hungary": "Венгрия",
    "Iceland": "Исландия",
    "India": "Индия",
    "Indonesia": "Индонезия",
    "Iran": "Иран",
    "Iraq": "Ирак",
    "Ireland": "Ирландия",
    "Israel": "Израиль",
    "Italy": "Италия",
    "Jamaica": "Ямайка",
    "Japan": "Япония",
    "Jordan": "Иордания",
    "Kazakhstan": "Казахстан",
    "Kuwait": "Кувейт",
    "Latvia": "Латвия",
    "Lebanon": "Ливан",
    "Lithuania": "Литва",
    "Luxembourg": "Люксембург",
    "Malaysia": "Малайзия",
    "Malta": "Мальта",
    "Mexico": "Мексика",
    "Morocco": "Марокко",
    "Nepal": "Непал",
    "Netherlands": "Нидерланды",
    "New Zealand": "Новая Зеландия",
    "Nigeria": "Нигерия",
    "Norway": "Норвегия",
    "Oman": "Оман",
    "Pakistan": "Пакистан",
    "Poland": "Польша",
    "Portugal": "Португалия",
    "Qatar": "Катар",
    "Romania": "Румыния",
    "Russia": "Россия",
    "Saudi Arabia": "Саудовская Аравия",
    "Serbia": "Сербия",
    "Singapore": "Сингапур",
    "Slovakia": "Словакия",
    "Slovenia": "Словения",
    "South Africa": "Южная Африка",
    "South Korea": "Южная Корея",
    "Spain": "Испания",
    "Sweden": "Швеция",
    "Switzerland": "Швейцария",
    "Taiwan": "Тайвань",
    "Thailand": "Таиланд",
    "Tunisia": "Тунис",
    "Turkey": "Турция",
    "Uganda": "Уганда",
    "United Arab Emirates": "Объединённые Арабские Эмираты",
    "United Kingdom": "Великобритания",
    "United States": "США",
    "Uruguay": "Уругвай",
    "Vietnam": "Вьетнам",
}

COUNTRY_ISO = {
    "Algeria": "DZ", "Argentina": "AR", "Australia": "AU", "Austria": "AT",
    "Bangladesh": "BD", "Belgium": "BE", "Brazil": "BR", "Cameroon": "CM",
    "Canada": "CA", "Chile": "CL", "China": "CN", "Colombia": "CO",
    "Croatia": "HR", "Cyprus": "CY", "Czechia": "CZ", "Denmark": "DK",
    "Egypt": "EG", "Estonia": "EE", "Ethiopia": "ET", "Finland": "FI",
    "France": "FR", "Germany": "DE", "Ghana": "GH", "Greece": "GR",
    "Hungary": "HU", "Iceland": "IS", "India": "IN", "Indonesia": "ID",
    "Iran": "IR", "Iraq": "IQ", "Ireland": "IE", "Israel": "IL",
    "Italy": "IT", "Jamaica": "JM", "Japan": "JP", "Jordan": "JO",
    "Kazakhstan": "KZ", "Kuwait": "KW", "Latvia": "LV", "Lebanon": "LB",
    "Lithuania": "LT", "Luxembourg": "LU", "Malaysia": "MY", "Malta": "MT",
    "Mexico": "MX", "Morocco": "MA", "Nepal": "NP", "Netherlands": "NL",
    "New Zealand": "NZ", "Nigeria": "NG", "Norway": "NO", "Oman": "OM",
    "Pakistan": "PK", "Poland": "PL", "Portugal": "PT", "Qatar": "QA",
    "Romania": "RO", "Russia": "RU", "Saudi Arabia": "SA", "Serbia": "RS",
    "Singapore": "SG", "Slovakia": "SK", "Slovenia": "SI", "South Africa": "ZA",
    "South Korea": "KR", "Spain": "ES", "Sweden": "SE", "Switzerland": "CH",
    "Taiwan": "TW", "Thailand": "TH", "Tunisia": "TN", "Turkey": "TR",
    "Uganda": "UG", "United Arab Emirates": "AE", "United Kingdom": "GB",
    "United States": "US", "Uruguay": "UY", "Vietnam": "VN",
}


def university_name(value):
    return UNIVERSITY_RU.get(str(value), str(value))


def field_name(value):
    return FIELD_RU.get(str(value), str(value))


def country_name(value):
    return COUNTRY_RU.get(str(value), str(value))


@st.cache_data(show_spinner=False)
def country_flag_data_url(value):
    code = COUNTRY_ISO.get(str(value))
    flag_path = FLAG_DIR / f"{code.lower()}.svg" if code else None
    if not flag_path or not flag_path.exists():
        return ""
    encoded = base64.b64encode(flag_path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def country_badges(values):
    badges = []
    for value in values:
        image = country_flag_data_url(value)
        if image:
            badges.append(
                f'<span class="country-badge"><img src="{image}" alt="">'
                f'<span>{escape(country_name(value))}</span></span>'
            )
    return f'<div class="country-badges">{"".join(badges)}</div>' if badges else ""


def country_label(value):
    return country_name(value)


@st.cache_data(show_spinner="Загружаю таблицу CWTS…")
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Не найден файл данных: {DATA_PATH}")
    data = pd.read_parquet(DATA_PATH)
    if "PP_hybrid_OA_OA_ub" in data.columns and "PP_hybrid_OA_ub" not in data.columns:
        data = data.rename(columns={"PP_hybrid_OA_OA_ub": "PP_hybrid_OA_ub"})
    for column in ["University", "ROR_ID", "Country", "Field", "Period"]:
        data[column] = data[column].astype("string")
    data["University display"] = data["University"].map(university_name)
    data["Country display"] = data["Country"].map(country_name)
    return data


def fmt(metric, value):
    if pd.isna(value):
        return "—"
    if metric in RATE_META:
        return f"{value:.1%}"
    if metric in AVERAGE_META:
        return f"{value:.2f}"
    return f"{value:,.0f}"


def aggregate_metric(frame, metric, group_column):
    """Aggregate a metric by its source numerator/denominator when it is a rate."""
    return aggregate_by(frame, metric, [group_column])


def aggregate_by(frame, metric, group_columns):
    if isinstance(group_columns, str):
        group_columns = [group_columns]
    if frame.empty:
        return pd.DataFrame(columns=[*group_columns, "value"])
    if metric in RATE_META:
        numerator, denominator = RATE_META[metric]
        grouped = frame.groupby(group_columns, observed=True)[[numerator, denominator]].sum(min_count=1)
        values = grouped[numerator].div(grouped[denominator])
    elif metric in AVERAGE_META:
        numerator, denominator = AVERAGE_META[metric]
        grouped = frame.groupby(group_columns, observed=True)[[numerator, denominator]].sum(min_count=1)
        values = grouped[numerator].div(grouped[denominator])
    else:
        values = frame.groupby(group_columns, observed=True)[metric].sum(min_count=1)
    return values.rename("value").reset_index()


def selection_frame(data, period, field, count_mode):
    return data[
        data["Period"].eq(period)
        & data["Field"].eq(field)
        & data["Frac_counting"].eq(count_mode)
    ].copy()


def show_table(frame, metric, metric_label, show_delta=False, selected_period_start=None):
    if frame.empty:
        st.info("Для выбранных условий нет строк, которые проходят порог публикаций.")
        return
    columns = {
        "Флаг": frame["Country"].map(country_flag_data_url).astype(str).to_list(),
        "Место в России": frame["Russia rank"].astype(int).to_list(),
        "Место в мире": frame["World rank"].astype(int).to_list(),
        "Университет": frame["University display"].astype(str).to_list(),
        "Страна": frame["Country"].map(country_name).astype(str).to_list(),
    }
    if metric != "P":
        columns["Публикации P"] = frame["P"].astype(float).to_list()
    columns[metric_label] = frame[metric].astype(float).to_list()
    if metric in CI_META:
        lower, upper = CI_META[metric]
        columns["Нижняя граница"] = frame[lower].astype(float).to_list()
        columns["Верхняя граница"] = frame[upper].astype(float).to_list()
    if show_delta and selected_period_start and selected_period_start > 2006 and "delta" in frame:
        if metric in RATE_META:
            columns["Изменение к предыдущему окну"] = frame["delta"].map(
                lambda value: "—" if pd.isna(value) else f"{value * 100:+.1f} п.п."
            ).to_list()
        else:
            columns["Изменение к предыдущему окну"] = frame["delta"].map(
                lambda value: "—" if pd.isna(value) else f"{value:+,.0f}"
            ).to_list()
    column_config = {
        "Флаг": st.column_config.ImageColumn("Флаг", width=42, help="Флаг страны университета."),
        "Место в России": st.column_config.NumberColumn("Место в России", format="%d", width="small"),
        "Место в мире": st.column_config.NumberColumn("Место в мире", format="%d", width="small"),
        "Университет": st.column_config.TextColumn("Университет", width="large"),
        "Страна": st.column_config.TextColumn("Страна", width="medium"),
    }
    if metric != "P":
        column_config["Публикации P"] = st.column_config.NumberColumn("Публикации P", format="%.1f", width="small")
    metric_format = "percent" if metric in RATE_META else "%.2f" if metric in AVERAGE_META else "%.1f"
    column_config[metric_label] = st.column_config.NumberColumn(metric_label, format=metric_format, width="medium")
    if metric in CI_META:
        interval_format = "percent" if metric in RATE_META else "%.2f"
        column_config["Нижняя граница"] = st.column_config.NumberColumn("Нижняя граница", format=interval_format, width="small")
        column_config["Верхняя граница"] = st.column_config.NumberColumn("Верхняя граница", format=interval_format, width="small")
    st.dataframe(
        pd.DataFrame(columns),
        hide_index=True,
        use_container_width=True,
        height=min(620, max(230, 42 * len(frame) + 38)),
        column_config=column_config,
    )


if not DATA_PATH.exists():
    st.error("Не найден файл данных. Проверьте, что рядом с app.py есть data/ranking_2026.parquet.")
    st.stop()

data = load_data()
period_options = data.sort_values("PeriodStart")["Period"].drop_duplicates().astype(str).tolist()
field_options = [field for field in FIELD_ORDER if field in set(data["Field"].astype(str))]
country_options = sorted(data["Country"].astype(str).unique())

logo_data_url = ""
if LOGO_PATH.exists():
    logo_data_url = f"data:image/jpeg;base64,{base64.b64encode(LOGO_PATH.read_bytes()).decode('ascii')}"
st.markdown(
    f'<div class="brand-header"><img src="{logo_data_url}" alt="Логотип «Выше квартилей">'
    '<div><h1>CWTS Leiden Ranking 2026</h1>'
    '<p class="hero-note">Научный результат без одного «общего балла»: сравнивайте объём, цитируемость, сотрудничество, открытый доступ и авторства.</p></div></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-attribution"><b>Расчёты Наукометрического центра НИУ ВШЭ</b> для Telegram-канала '
    '<a href="https://t.me/HQhse" target="_blank" rel="noopener noreferrer">«Выше квартилей»</a>. '
    'При подготовке дашборда и аналитического текста использовалась модель OpenAI GPT‑6; числовые значения рассчитаны по выгрузке CWTS.</div>',
    unsafe_allow_html=True,
)

st.markdown("### Настройки выборки")
filter_row_1 = st.columns([1.1, 1.5, 1.15, 1.6])
with filter_row_1[0]:
    selected_period = st.selectbox("Период публикаций", period_options, index=len(period_options) - 1)
with filter_row_1[1]:
    selected_field = st.selectbox("Область", field_options, index=0, format_func=field_name)
with filter_row_1[2]:
    metric_group = st.selectbox("Измерение", list(METRICS))
with filter_row_1[3]:
    metric_options = list(METRICS[metric_group])
    metric_label = st.selectbox("Показатель", metric_options, index=0, key=f"metric_label_{metric_group}")
    metric = METRICS[metric_group][metric_label]

filter_row_2 = st.columns([1.35, 1.25, 2.75])
with filter_row_2[0]:
    if metric_group == "Научное влияние":
        method_label = st.radio(
            "Подсчёт",
            ["Дробный", "Полный"],
            index=0,
            horizontal=True,
            help="Дробный подсчёт распределяет публикацию между организациями соавторов; CWTS рекомендует его для сравнения влияния.",
        )
        count_mode = 1 if method_label == "Дробный" else 0
    else:
        count_mode = 0
        st.caption("Для этого измерения CWTS использует полный подсчёт.")
with filter_row_2[1]:
    minimum_publications = st.selectbox(
        "Минимум публикаций",
        [0, 50, 100, 500, 1000, 5000, 10000],
        index=2,
        format_func=lambda value: "Без минимума" if value == 0 else f"{value:,}".replace(",", " "),
    )
with filter_row_2[2]:
    st.caption("По умолчанию выбран порог 100 публикаций. В срез входят все прошедшие его университеты; доступны все области и последний опубликованный период.")

st.caption(
    f"Выпуск опубликован 4 ноября 2026 года · последнее окно — {period_options[-1]} · "
    "источник — выгрузка CWTS из Web of Science."
)

current = selection_frame(data, selected_period, selected_field, count_mode)
current = current[current["P"].ge(minimum_publications) & current[metric].notna()].copy()
selected_period_start = int(current["PeriodStart"].iloc[0]) if not current.empty else int(
    data.loc[data["Period"].eq(selected_period), "PeriodStart"].iloc[0]
)
metric_percent = metric in RATE_META
metric_title = metric_label

flag_ru = country_flag_data_url("Russia")
comparison_flags = [
    country_flag_data_url(country)
    for country in ["China", "United States", "Russia", "India"]
]
comparison_backgrounds = ", ".join(f'url("{flag}")' for flag in comparison_flags)
st.markdown(
    f"""<style>
      [data-testid="stTabs"] [role="tab"][id$="-tab-1"]::before {{
        content: ""; display: inline-block; width: 22px; height: 15px; margin-right: .45rem;
        vertical-align: middle; background: url("{flag_ru}") center / contain no-repeat;
        border-radius: 2px; box-shadow: 0 0 0 1px #8290a0;
      }}
      [data-testid="stTabs"] [role="tab"][id$="-tab-2"]::before {{
        content: ""; display: inline-block; width: 70px; height: 15px; margin-right: .45rem;
        vertical-align: middle; background-image: {comparison_backgrounds};
        background-repeat: no-repeat; background-size: 16px 11px;
        background-position: 0 center, 18px center, 36px center, 54px center;
        border-radius: 2px; filter: drop-shadow(0 0 1px #8290a0);
      }}
    </style>""",
    unsafe_allow_html=True,
)
world_tab, russia_tab, trends_tab, organizations_tab, method_tab = st.tabs(
    ["🌍 Общий рейтинг", "Россия", "Страновые сравнения", "🏛 Сравнение организаций", "ℹ️ Методика"]
)


with world_tab:
    if current.empty:
        st.warning("Нет данных для выбранной комбинации. Уменьшите порог публикаций или выберите другую область.")
    else:
        top = current.sort_values(metric, ascending=False, na_position="last").copy()
        top["World rank"] = top[metric].rank(method="min", ascending=False).astype(int)
        top["Russia rank"] = pd.NA
        k1, k2, k3 = st.columns(3)
        k1.metric("Университетов", f"{current['University'].nunique():,}".replace(",", " "))
        k2.metric("Стран и территорий", f"{current['Country'].nunique():,}".replace(",", " "))
        k3.metric(f"Максимум · {metric_title}", fmt(metric, top.iloc[0][metric]))
        st.caption(f"Лидер: **{university_name(top.iloc[0]['University'])}** · {country_label(top.iloc[0]['Country'])}.")

        st.subheader("Лидеры по выбранному показателю")
        top20 = top.head(20).copy()
        top20_countries = sorted(top20["Country display"].dropna().unique().tolist())
        country_palette = px.colors.qualitative.Alphabet
        country_color_map = {
            country: country_palette[index % len(country_palette)]
            for index, country in enumerate(top20_countries)
        }
        fig = px.bar(
            top20,
            x=metric,
            y="University display",
            orientation="h",
            color="Country display",
            hover_data={"Country display": True, "P": ":,.1f", metric: ":.3f" if metric_percent else ":,.2f"},
            labels={metric: metric_title, "University display": "Университет", "Country display": "Страна", "P": "P"},
            color_discrete_map=country_color_map,
            category_orders={"Country display": top20_countries},
        )
        fig.update_yaxes(categoryorder="array", categoryarray=top20["University display"].tolist(), autorange="reversed")
        if metric_percent:
            fig.update_xaxes(tickformat=".0%")
        else:
            fig.update_xaxes(tickformat=",.0f")
        fig.update_layout(
            height=690,
            showlegend=True,
            legend=dict(title="Страна", orientation="v", y=1, yanchor="top", x=1.02, xanchor="left", font=dict(size=11)),
            margin=dict(l=10, r=175, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Цвет столбца обозначает страну; легенда справа, полное название страны доступно и при наведении на столбец.")

        st.subheader("Таблица университетов")
        filter_cols = st.columns([1.35, 1.6, 0.75])
        with filter_cols[0]:
            table_search = st.text_input("Поиск по вузу", placeholder="Название на русском или английском", key="world_table_search")
        with filter_cols[1]:
            table_countries = st.multiselect(
                "Страны",
                country_options,
                default=[],
                format_func=country_label,
                help="Пустой выбор показывает все страны.",
                key="world_table_countries",
            )
            if table_countries:
                st.markdown(country_badges(table_countries), unsafe_allow_html=True)
        with filter_cols[2]:
            table_limit = st.selectbox(
                "Строк",
                [50, 100, 250, 500, 0],
                index=1,
                format_func=lambda value: "Все" if value == 0 else str(value),
                key="world_table_limit",
            )
        filtered_table = top.copy()
        if table_countries:
            filtered_table = filtered_table[filtered_table["Country"].isin(table_countries)]
        if table_search.strip():
            query = table_search.strip()
            matches = filtered_table["University display"].str.contains(query, case=False, regex=False, na=False)
            matches |= filtered_table["University"].str.contains(query, case=False, regex=False, na=False)
            filtered_table = filtered_table[matches]
        table_rows = filtered_table if table_limit == 0 else filtered_table.head(table_limit)
        display = pd.DataFrame({
            "Место": table_rows["World rank"].astype(int),
            "Университет": table_rows["University display"].astype(str),
            "Флаг": table_rows["Country"].map(country_flag_data_url).astype(str),
            "Страна": table_rows["Country"].map(country_name).astype(str),
        })
        if metric != "P":
            display["Публикации P"] = table_rows["P"].astype(float)
        display[metric_title] = table_rows[metric].astype(float)
        if metric in CI_META:
            lower, upper = CI_META[metric]
            display["Интервал устойчивости"] = [
                f"{fmt(metric, lo)}–{fmt(metric, hi)}" for lo, hi in zip(table_rows[lower], table_rows[upper])
            ]
        table_config = {
            "Место": st.column_config.NumberColumn("Место", format="%d", width="small"),
            "Университет": st.column_config.TextColumn("Университет", width="large"),
            "Флаг": st.column_config.ImageColumn("Флаг", width=42, help="Флаг страны университета."),
            "Страна": st.column_config.TextColumn("Страна", width="medium"),
        }
        if metric != "P":
            table_config["Публикации P"] = st.column_config.NumberColumn("Публикации P", format="%.1f", width="small")
        display_format = "percent" if metric in RATE_META else "%.2f" if metric in AVERAGE_META else "%.1f"
        table_config[metric_title] = st.column_config.NumberColumn(metric_title, format=display_format, width="medium")
        if metric in CI_META:
            table_config["Интервал устойчивости"] = st.column_config.TextColumn("Интервал устойчивости", width="medium")
        st.caption(f"Показано {len(table_rows)} из {len(filtered_table)} вузов после фильтрации.")
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            height=min(620, max(260, 42 * len(table_rows) + 38)),
            column_config=table_config,
        )

        st.caption("Страновые суммы на этой вкладке убраны: показатели организаций нельзя без оговорок трактовать как число уникальных публикаций.")

        export = filtered_table.copy()
        export.insert(0, "Место по показателю", export["World rank"].astype(int))
        export["Университет"] = export["University display"]
        export["Страна"] = export["Country"].map(country_label)
        export["Область"] = export["Field"].map(field_name)
        export["Период"] = export["Period"].astype(str)
        export[metric_title] = export[metric].map(lambda value: fmt(metric, value))
        export_cols = ["Место по показателю", "Университет", "Страна", "Область", "Период", "P", metric_title]
        csv = export[export_cols].to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Скачать текущую выборку (CSV)",
            data=csv,
            file_name=f"leiden_2026_{selected_period_start}_{metric}.csv",
            mime="text/csv",
        )


with russia_tab:
    current_global = selection_frame(data, selected_period, selected_field, count_mode)
    current_global = current_global[current_global["P"].ge(minimum_publications) & current_global[metric].notna()].copy()
    russia = current_global[current_global["Country"].eq("Russia")].copy()
    st.subheader(f"Российские университеты · {field_name(selected_field)} · {selected_period}")
    if russia.empty:
        st.info("В российской выборке нет вузов, прошедших выбранный порог публикаций.")
    else:
        ranked = current_global.sort_values(metric, ascending=False).copy()
        ranked["World rank"] = ranked[metric].rank(method="min", ascending=False).astype(int)
        russia = ranked[ranked["Country"].eq("Russia")].copy().sort_values(metric, ascending=False)
        russia["Russia rank"] = range(1, len(russia) + 1)

        prev_start = selected_period_start - 1
        if selected_period_start > 2006:
            previous = data[
                data["PeriodStart"].eq(prev_start)
                & data["Field"].eq(selected_field)
                & data["Frac_counting"].eq(count_mode)
            ][["University", metric]].copy()
            previous_map = previous.drop_duplicates("University").set_index("University")[metric]
            russia["delta"] = russia[metric] - russia["University"].map(previous_map)

        r1, r2, r3 = st.columns(3)
        r1.metric("Университетов в выборке", f"{russia['University'].nunique():,}".replace(",", " "))
        r2.metric("Лидер по показателю", university_name(russia.iloc[0]["University"]))
        r3.metric(f"Значение лидера · {metric_title}", fmt(metric, russia.iloc[0][metric]))

        chart_data = russia.sort_values(metric, ascending=False).copy()
        fig = px.bar(
            chart_data,
            x=metric,
            y="University display",
            orientation="h",
            hover_data={"P": ":,.1f", metric: ":.3f" if metric_percent else ":,.2f"},
            labels={metric: metric_title, "University display": "Университет"},
            color=metric,
            color_continuous_scale=["#c7e0fa", "#2e6fb0"],
        )
        fig.update_yaxes(categoryorder="array", categoryarray=chart_data["University display"].tolist(), autorange="reversed")
        if metric in CI_META:
            low, high = CI_META[metric]
            fig.update_traces(
                error_x={
                    "type": "data",
                    "symmetric": False,
                    "array": (chart_data[high] - chart_data[metric]).clip(lower=0),
                    "arrayminus": (chart_data[metric] - chart_data[low]).clip(lower=0),
                }
            )
        if metric_percent:
            fig.update_xaxes(tickformat=".0%")
        else:
            fig.update_xaxes(tickformat=",.0f")
        fig.update_layout(height=max(560, 28 * len(chart_data) + 100), coloraxis_showscale=False, margin=dict(l=10, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
        if metric in CI_META:
            st.caption("Усы показывают 95%-ные интервалы устойчивости CWTS; это не интервалы для всего российского сектора.")
        st.caption("Изменение в таблице сравнивается с предыдущим перекрывающимся окном, если оно доступно.")
        st.subheader("Российские университеты: таблица мест")
        ru_search = st.text_input("Найти вуз", placeholder="Название на русском или английском", key="russia_table_search")
        ru_table = russia.copy()
        if ru_search.strip():
            ru_query = ru_search.strip()
            ru_matches = ru_table["University display"].str.contains(ru_query, case=False, regex=False, na=False)
            ru_matches |= ru_table["University"].str.contains(ru_query, case=False, regex=False, na=False)
            ru_table = ru_table[ru_matches]
        show_table(ru_table, metric, metric_title, show_delta=True, selected_period_start=selected_period_start)

        st.subheader("Карточки российских университетов")
        st.caption(
            "Короткая карточка показывает место и выбранный показатель. Нажмите «Все показатели», "
            "чтобы раскрыть профиль. Для текущих фильтров автоматически выбраны пять лидеров; список можно изменить."
        )
        profile_options = russia.sort_values("Russia rank")["University"].astype(str).tolist()
        profile_scope = (selected_period, selected_field, count_mode, minimum_publications, metric)
        if st.session_state.get("russia_profile_scope") != profile_scope:
            st.session_state["russia_profile_universities"] = profile_options[:5]
            st.session_state["russia_profile_scope"] = profile_scope
        selected_profiles = st.multiselect(
            "Вузы в карточках и динамике",
            profile_options,
            format_func=university_name,
            key="russia_profile_universities",
        )
        impact_profile = selection_frame(data, selected_period, selected_field, 1)
        full_profile = selection_frame(data, selected_period, selected_field, 0)
        impact_profile = impact_profile[impact_profile["Country"].eq("Russia")].drop_duplicates("University").set_index("University")
        full_profile = full_profile[full_profile["Country"].eq("Russia")].drop_duplicates("University").set_index("University")
        current_profile = russia.drop_duplicates("University").set_index("University")
        card_columns = st.columns(2)
        for card_index, university in enumerate(selected_profiles):
            if university not in current_profile.index:
                continue
            row = current_profile.loc[university]
            with card_columns[card_index % 2]:
                with st.container(border=True):
                    st.markdown(f"#### {university_name(university)}")
                    st.caption(
                        f"Место в России: {int(row['Russia rank'])} · место в мире: {int(row['World rank'])} · "
                        f"{field_name(selected_field)} · {selected_period}"
                    )
                    delta_value = row.get("delta", float("nan"))
                    if pd.isna(delta_value):
                        delta_label = None
                    elif metric in RATE_META:
                        delta_label = f"{delta_value * 100:+.1f} п.п. к предыдущему окну"
                    elif metric in AVERAGE_META:
                        delta_label = f"{delta_value:+.2f} к предыдущему окну"
                    else:
                        delta_label = f"{delta_value:+,.0f} к предыдущему окну".replace(",", " ")
                    st.metric(metric_title, fmt(metric, row[metric]), delta=delta_label, delta_color="off")
                    with st.expander("Все показатели", expanded=False):
                        for group_name, group_metrics in METRICS.items():
                            source_rows = impact_profile if group_name == "Научное влияние" else full_profile
                            st.markdown(f"**{group_name}** · {'дробный подсчёт' if group_name == 'Научное влияние' else 'полный подсчёт'}")
                            if university not in source_rows.index:
                                st.caption("Для выбранных условий нет значений.")
                                continue
                            source_row = source_rows.loc[university]
                            metric_items = list(group_metrics.items())
                            for offset in range(0, len(metric_items), 2):
                                metric_columns = st.columns(2)
                                for metric_column, (indicator_label, indicator) in zip(metric_columns, metric_items[offset:offset + 2]):
                                    indicator_value = source_row.get(indicator, float("nan"))
                                    metric_column.metric(indicator_label, fmt(indicator, indicator_value))
                                    if indicator in CI_META:
                                        lower, upper = CI_META[indicator]
                                        if lower in source_row.index and upper in source_row.index:
                                            metric_column.caption(
                                                f"95%: {fmt(indicator, source_row[lower])}–{fmt(indicator, source_row[upper])}"
                                            )

        if selected_profiles:
            st.subheader(f"Динамика · {metric_title}")
            st.caption(
                "График использует те же область, показатель и способ подсчёта, что и фильтры в шапке; "
                "выбранный период задаёт конечную точку ряда."
            )
            profile_trend = data[
                data["Field"].eq(selected_field)
                & data["Frac_counting"].eq(count_mode)
                & data["University"].isin(selected_profiles)
                & data["PeriodStart"].le(selected_period_start)
                & data[metric].notna()
            ].copy()
            if profile_trend.empty:
                st.info("Для выбранных вузов и показателя нет исторических значений.")
            else:
                profile_trend["Университет"] = profile_trend["University"].map(university_name)
                profile_trend["Окно"] = profile_trend["Period"].astype(str)
                profile_period_order = data.loc[data["PeriodStart"].le(selected_period_start), ["PeriodStart", "Period"]].drop_duplicates().sort_values("PeriodStart")["Period"].astype(str).tolist()
                profile_fig = px.line(
                    profile_trend,
                    x="Окно",
                    y=metric,
                    color="Университет",
                    markers=True,
                    category_orders={"Окно": profile_period_order},
                    labels={"Окно": "Период публикаций", metric: metric_title},
                    color_discrete_sequence=["#2e6fb0", "#e08a36", "#4a9568", "#8a66a8", "#c45b5b", "#548b9d"],
                )
                if metric in RATE_META:
                    profile_fig.update_yaxes(tickformat=".0%")
                elif metric not in AVERAGE_META:
                    profile_fig.update_yaxes(tickformat=",.0f")
                profile_fig.update_layout(height=460, hovermode="x unified", margin=dict(l=10, r=20, t=20, b=20), legend_title_text="")
                st.plotly_chart(profile_fig, use_container_width=True)

                first_profile_period = int(profile_trend["PeriodStart"].min())
                first_profile_values = profile_trend[profile_trend["PeriodStart"].eq(first_profile_period)].drop_duplicates("University").set_index("University")[metric]
                latest_profile_values = profile_trend[profile_trend["PeriodStart"].eq(selected_period_start)].drop_duplicates("University").set_index("University")[metric]
                summary_columns = st.columns(3)
                for profile_index, university in enumerate(selected_profiles):
                    first_value = first_profile_values.get(university, float("nan"))
                    latest_value = latest_profile_values.get(university, float("nan"))
                    change_value = latest_value - first_value if pd.notna(latest_value) and pd.notna(first_value) else float("nan")
                    if pd.isna(change_value):
                        change_label = "—"
                    elif metric in RATE_META:
                        change_label = f"{change_value * 100:+.1f} п.п."
                    elif metric in AVERAGE_META:
                        change_label = f"{change_value:+.2f}"
                    else:
                        change_label = f"{change_value:+,.1f}".replace(",", " ")
                    with summary_columns[profile_index % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{university_name(university)}**")
                            first_col, latest_col, change_col = st.columns(3)
                            first_col.metric("Начало", fmt(metric, first_value))
                            latest_col.metric(selected_period, fmt(metric, latest_value))
                            change_col.metric("Изменение", change_label, delta_color="off")
                st.caption("Начальная точка — первое доступное окно; четырёхлетние окна перекрываются на три года.")

    st.subheader(f"Динамика по научным областям · {metric_title}")
    ru_history = data[
        data["Country"].eq("Russia")
        & data["Field"].ne("All sciences")
        & data["Frac_counting"].eq(count_mode)
        & data[metric].notna()
    ].copy()
    if minimum_publications:
        latest_eligible = ru_history[
            ru_history["Period"].eq(period_options[-1]) & ru_history["P"].ge(minimum_publications)
        ][["University", "Field"]].drop_duplicates()
        ru_history = ru_history.merge(latest_eligible.assign(_eligible=True), on=["University", "Field"], how="inner")

    if ru_history.empty:
        st.info("Для выбранного показателя нет российской динамики по областям.")
    else:
        field_series = aggregate_by(ru_history, metric, ["PeriodStart", "Period", "Field"])
        field_series["Область"] = field_series["Field"].map(field_name)
        order = data[["PeriodStart", "Period"]].drop_duplicates().sort_values("PeriodStart")
        period_order = order["Period"].astype(str).tolist()
        field_series["Период"] = field_series["Period"].astype(str)
        field_fig = px.line(
            field_series,
            x="Период",
            y="value",
            color="Область",
            markers=True,
            category_orders={"Период": period_order},
            labels={"Период": "Окно публикаций", "value": metric_title, "Область": "Научная область"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        if metric in RATE_META:
            field_fig.update_yaxes(tickformat=".0%")
        elif metric not in AVERAGE_META:
            field_fig.update_yaxes(tickformat=",.0f")
        field_fig.update_layout(height=500, hovermode="x unified", margin=dict(l=10, r=20, t=20, b=20))
        st.plotly_chart(field_fig, use_container_width=True)

        first_start = int(order["PeriodStart"].min())
        latest_start = int(order["PeriodStart"].max())
        previous_start = int(order["PeriodStart"].nlargest(2).iloc[-1]) if len(order) > 1 else latest_start
        first_values = field_series[field_series["PeriodStart"].eq(first_start)][["Field", "value"]].rename(columns={"value": "first"})
        latest_values = field_series[field_series["PeriodStart"].eq(latest_start)][["Field", "value"]].rename(columns={"value": "latest"})
        previous_values = field_series[field_series["PeriodStart"].eq(previous_start)][["Field", "value"]].rename(columns={"value": "previous"})
        summary = first_values.merge(latest_values, on="Field", how="inner").merge(previous_values, on="Field", how="left")
        summary["Область"] = summary["Field"].map(field_name)

        def change_text(value):
            if pd.isna(value):
                return "—"
            if metric in RATE_META:
                return f"{value * 100:+.1f} п.п."
            if metric in AVERAGE_META:
                return f"{value:+.2f}"
            return f"{value:+,.0f}".replace(",", " ")

        summary_table = pd.DataFrame({
            "Область": summary["Область"],
            "2006–2009": summary["first"].map(lambda value: fmt(metric, value)),
            f"{period_options[-1]}": summary["latest"].map(lambda value: fmt(metric, value)),
            "Изменение с 2006–2009": (summary["latest"] - summary["first"]).map(change_text),
            f"К окну {previous_start}–{previous_start + 3}": (summary["latest"] - summary["previous"]).map(change_text),
        })
        st.dataframe(summary_table, hide_index=True, use_container_width=True)
        st.caption(
            "Агрегат по российским университетам рассчитан суммированием числителя и знаменателя показателя. "
            "Соседние четырёхлетние окна перекрываются на три года; их разница не является годовым темпом."
        )
        if metric in RATE_META and not summary.empty:
            best = summary.sort_values("latest").iloc[-1]
            largest_gain = summary.assign(gain=summary["latest"] - summary["first"]).sort_values("gain").iloc[-1]
            st.info(
                f"В последнем окне наибольшее значение у области «{best['Область']}» "
                f"({fmt(metric, best['latest'])}); сильнее всего показатель вырос с 2006–2009 "
                f"в области «{largest_gain['Область']}» — {change_text(largest_gain['gain'])}."
            )


with trends_tab:
    st.caption(
        f"Графики используют область, конечный период, способ подсчёта и минимальный объём из общей шапки: "
        f"{field_name(selected_field)} · до {selected_period} · "
        f"{'дробный' if count_mode == 1 else 'полный'} подсчёт · "
        f"порог P: {'без минимума' if minimum_publications == 0 else f'{minimum_publications:,}'.replace(',', ' ')}. "
        f"Второй критерий ранжирования и показатель долей — «{metric_title}»."
    )
    default_compare_countries = [name for name in ["China", "United States", "Russia", "India"] if name in country_options]
    compared_countries = st.multiselect(
        "Страны для сравнения",
        country_options,
        default=default_compare_countries,
        format_func=country_label,
        help="Выберите любые страны из рейтинга. Один список управляет обоими аналитическими блоками ниже.",
        key="country_comparison_selection",
    )
    if compared_countries:
        st.markdown(country_badges(compared_countries), unsafe_allow_html=True)
    comparison_data = data[
        data["Field"].eq(selected_field)
        & data["Frac_counting"].eq(count_mode)
        & data["PeriodStart"].le(selected_period_start)
        & data[metric].notna()
    ].copy()
    comparison_data = comparison_data[comparison_data["P"].ge(minimum_publications)].copy()
    if not compared_countries:
        st.info("Выберите хотя бы одну страну: набор будет применён к обоим аналитическим блокам.")
    elif comparison_data.empty:
        st.info("Для выбранных фильтров нет данных. Уменьшите порог публикаций или измените область/показатель.")
    else:
        top_n_max = int(
            comparison_data.groupby("PeriodStart", observed=True)["University"].nunique().min()
        )
        top_n_default = min(10, max(1, top_n_max))
        if st.session_state.get("country_top_n", top_n_default) > top_n_max:
            st.session_state["country_top_n"] = top_n_default
        top_n_spacer, top_n_control, top_n_title = st.columns([0.25, 1, 2.6])
        with top_n_control:
            top_n = st.number_input(
                "Размер топа",
                min_value=1,
                max_value=max(1, top_n_max),
                value=top_n_default,
                step=1,
                key="country_top_n",
                help="Можно задать любое целое число. Верхний предел — число вузов, доступных во всех окнах сравнения.",
            )
        with top_n_title:
            st.subheader(f"Кто входит в топ-{top_n}: объём и выбранный показатель")
        st.caption(
            f"Сравнение обновляется по фильтрам общей шапки. Второй критерий — «{metric_title}»; "
            "при выборе P остаётся только один критерий, чтобы не дублировать линию."
        )
        topn_rows = []
        criteria = [("По объёму публикаций P", "P")]
        if metric != "P":
            criteria.append((f"По показателю: {metric_title}", metric))
        for period_start, period_group in comparison_data.groupby("PeriodStart", observed=True):
            period_label = str(period_group["Period"].iloc[0])
            for rank_label, sort_metric in criteria:
                selected_top = period_group.dropna(subset=[sort_metric]).nlargest(top_n, sort_metric)
                for country in compared_countries:
                    topn_rows.append({
                        "PeriodStart": int(period_start),
                        "Окно": period_label,
                        "Критерий": rank_label,
                        "Страна": country_label(country),
                        "Число университетов": int(selected_top["Country"].eq(country).sum()),
                    })
        topn_composition = pd.DataFrame(topn_rows)
        category_order = topn_composition[["PeriodStart", "Окно"]].drop_duplicates().sort_values("PeriodStart")["Окно"].tolist()
        fig_topn_count = px.line(
            topn_composition,
            x="Окно",
            y="Число университетов",
            color="Страна",
            line_dash="Критерий",
            markers=True,
            category_orders={"Окно": category_order},
            color_discrete_sequence=px.colors.qualitative.Safe,
            labels={"Окно": "Окно публикаций"},
        )
        fig_topn_count.update_yaxes(
            dtick=1 if top_n <= 25 else None,
            nticks=8,
            rangemode="tozero",
        )
        fig_topn_count.update_layout(height=440, hovermode="x unified", margin=dict(l=10, r=20, t=20, b=20), legend_title_text="")
        st.plotly_chart(fig_topn_count, use_container_width=True)
        st.caption(
            f"В каждой точке — число университетов выбранной страны среди {top_n} лидеров в соответствующем окне. "
            "Минимум публикаций применяется отдельно к каждому окну."
        )

        # Rates and averages are represented by their source totals so country shares are
        # weighted correctly instead of adding university percentages or averages.
        if metric in RATE_META:
            comparison_component = RATE_META[metric][0]
            comparison_component_note = f"числителя {comparison_component}"
        elif metric in AVERAGE_META:
            comparison_component = AVERAGE_META[metric][0]
            comparison_component_note = f"суммарного компонента {comparison_component}"
        else:
            comparison_component = metric
            comparison_component_note = f"показателя {comparison_component}"
        if comparison_component == "P":
            comparison_component = "P_top_10"
            comparison_component_note = "публикаций в top 10% (ориентир вместо повторного P)"

        st.subheader("Доли стран в объёме публикаций и выбранном показателе")
        selected_geography = comparison_data[comparison_data["Country"].isin(compared_countries)]
        country_period = (
            selected_geography.groupby(["PeriodStart", "Period", "Country"], observed=True)[["P", comparison_component]]
            .sum(min_count=1)
            .reset_index()
        )
        world_period = (
            comparison_data.groupby(["PeriodStart", "Period"], observed=True)[["P", comparison_component]]
            .sum(min_count=1)
            .rename(columns={"P": "Общий объём выборки", comparison_component: "Общий компонент показателя"})
            .reset_index()
        )
        geography_chart = country_period.merge(world_period, on=["PeriodStart", "Period"])
        geography_chart["Доля объёма"] = geography_chart["P"] / geography_chart["Общий объём выборки"]
        geography_chart["Доля компонента показателя"] = geography_chart[comparison_component] / geography_chart["Общий компонент показателя"]
        geography_chart["Страна"] = geography_chart["Country"].map(country_label)
        geography_chart["Окно"] = geography_chart["Period"].astype(str)
        category_order = geography_chart[["PeriodStart", "Period"]].drop_duplicates().sort_values("PeriodStart")["Period"].astype(str).tolist()
        share_col_1, share_col_2 = st.columns(2)
        with share_col_1:
            fig_volume = px.line(
                geography_chart,
                x="Окно",
                y="Доля объёма",
                color="Страна",
                markers=True,
                category_orders={"Окно": category_order},
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={
                    "Окно": "Период публикаций",
                    "Доля объёма": "Доля в мире",
                    "Страна": "Страна",
                },
                hover_data={"Доля объёма": ":.2%", "Окно": True, "Страна": True},
            )
            fig_volume.update_yaxes(tickformat=".2%", rangemode="tozero", nticks=6)
            fig_volume.update_layout(
                height=390,
                title="Объём публикаций P",
                title_font_size=16,
                hovermode="x unified",
                margin=dict(l=20, r=10, t=55, b=35),
                legend_title_text="",
            )
            st.plotly_chart(fig_volume, use_container_width=True)
        with share_col_2:
            fig_top10 = px.line(
                geography_chart,
                x="Окно",
                y="Доля компонента показателя",
                color="Страна",
                markers=True,
                category_orders={"Окно": category_order},
                color_discrete_sequence=px.colors.qualitative.Safe,
                labels={
                    "Окно": "Период публикаций",
                    "Доля компонента показателя": "Доля в мире",
                    "Страна": "Страна",
                },
                hover_data={"Доля компонента показателя": ":.2%", "Окно": True, "Страна": True},
            )
            fig_top10.update_yaxes(tickformat=".2%", rangemode="tozero", nticks=6)
            fig_top10.update_layout(
                height=390,
                hovermode="x unified",
                title="Top 10% по цитируемости" if metric == "P" else "Выбранный показатель",
                title_font_size=16,
                margin=dict(l=20, r=10, t=55, b=35),
                legend_title_text="",
            )
            st.plotly_chart(fig_top10, use_container_width=True)
        st.caption(
            f"Доля P — вклад в суммарный P университетов рейтинга; второй график показывает долю "
            f"{comparison_component_note} для выбранного показателя «{metric_title}». "
            "Если показатель задан как доля или среднее, суммируется его исходный числитель/итог, а не сами проценты или средние. "
            f"Подсчёт: {'дробный' if count_mode == 1 else 'полный'}; при полном подсчёте совместные публикации могут учитываться у нескольких университетов."
        )


with organizations_tab:
    st.caption(
        f"Сравнивайте отдельные организации по выбранному показателю и местам во времени. Фильтры берутся из общей шапки: "
        f"{field_name(selected_field)} · до {selected_period} · "
        f"{'дробный' if count_mode == 1 else 'полный'} подсчёт · "
        f"порог P: {'без минимума' if minimum_publications == 0 else f'{minimum_publications:,}'.replace(',', ' ')}."
    )
    st.caption(
        "По умолчанию выбраны пять лидеров России в текущем срезе. Список можно менять и дополнять университетами из любых стран; "
        "после смены общих фильтров начальная пятёрка обновится."
    )
    organization_options = (
        data[["University", "University display"]]
        .drop_duplicates()
        .sort_values("University display")["University"]
        .astype(str)
        .tolist()
    )
    organization_country_map = (
        data.drop_duplicates("University").set_index("University")["Country"].to_dict()
    )

    def organization_option_label(value):
        country = organization_country_map.get(str(value), "")
        label = university_name(value)
        return f"{label} · {country_name(country)}" if country else label

    default_organizations = (
        current.loc[current["Country"].eq("Russia")]
        .sort_values(metric, ascending=False)["University"]
        .astype(str)
        .head(5)
        .tolist()
    )
    if not default_organizations and not current.empty:
        default_organizations = current.sort_values(metric, ascending=False)["University"].astype(str).head(5).tolist()
    organization_scope = (selected_period, selected_field, count_mode, minimum_publications, metric)
    if st.session_state.get("organization_comparison_scope") != organization_scope:
        st.session_state["organization_comparison_selection"] = default_organizations
        st.session_state["organization_comparison_scope"] = organization_scope
    selected_organizations = st.multiselect(
        "Организации для сравнения",
        organization_options,
        format_func=organization_option_label,
        key="organization_comparison_selection",
        help="Начните вводить название на русском или английском. Можно сравнивать российские и зарубежные организации вместе.",
    )

    if not selected_organizations:
        st.info("Выберите хотя бы одну организацию.")
    else:
        organization_history = data[
            data["Field"].eq(selected_field)
            & data["Frac_counting"].eq(count_mode)
            & data["PeriodStart"].le(selected_period_start)
            & data[metric].notna()
        ].copy()
        organization_history = organization_history[organization_history["P"].ge(minimum_publications)].copy()
        if organization_history.empty:
            st.info("Для выбранных условий нет данных. Уменьшите порог публикаций или измените область/показатель.")
        else:
            organization_history["World rank"] = (
                organization_history.groupby("PeriodStart", observed=True)[metric]
                .rank(method="min", ascending=False)
                .astype("Int64")
            )
            russian_history = organization_history[organization_history["Country"].eq("Russia")].copy()
            russian_history["Russia rank"] = (
                russian_history.groupby("PeriodStart", observed=True)[metric]
                .rank(method="min", ascending=False)
                .astype("Int64")
            )
            organization_history = organization_history.merge(
                russian_history[["University", "PeriodStart", "Russia rank"]],
                on=["University", "PeriodStart"],
                how="left",
            )
            selected_history = organization_history[
                organization_history["University"].isin(selected_organizations)
            ].copy()
            latest_selected = selected_history[
                selected_history["PeriodStart"].eq(selected_period_start)
            ].sort_values(metric, ascending=False)

            if latest_selected.empty:
                st.info("У выбранных организаций нет значений в последнем окне при текущем пороге публикаций.")
            else:
                table_columns = {
                    "Флаг": latest_selected["Country"].map(country_flag_data_url).astype(str).to_list(),
                    "Место в мире": latest_selected["World rank"].astype(int).to_list(),
                    "Место в России": [
                        int(value) if pd.notna(value) else None for value in latest_selected["Russia rank"]
                    ],
                    "Университет": latest_selected["University display"].astype(str).to_list(),
                    "Страна": latest_selected["Country"].map(country_name).astype(str).to_list(),
                    "Публикации P": latest_selected["P"].astype(float).to_list(),
                }
                if metric != "P":
                    table_columns[metric_title] = latest_selected[metric].astype(float).to_list()
                organization_table = pd.DataFrame(table_columns)
                organization_config = {
                    "Флаг": st.column_config.ImageColumn("Флаг", width=42),
                    "Место в мире": st.column_config.NumberColumn("Место в мире", format="%d", width="small"),
                    "Место в России": st.column_config.NumberColumn("Место в России", format="%d", width="small"),
                    "Университет": st.column_config.TextColumn("Университет", width="large"),
                    "Страна": st.column_config.TextColumn("Страна", width="medium"),
                    "Публикации P": st.column_config.NumberColumn("Публикации P", format="%.1f", width="small"),
                }
                if metric != "P":
                    metric_format = "percent" if metric in RATE_META else "%.2f" if metric in AVERAGE_META else "%.1f"
                    organization_config[metric_title] = st.column_config.NumberColumn(
                        metric_title,
                        format=metric_format,
                        width="medium",
                    )
                st.subheader(f"Срез за {selected_period}")
                st.dataframe(
                    organization_table,
                    hide_index=True,
                    use_container_width=True,
                    column_config=organization_config,
                )

            if selected_history.empty:
                st.info("У выбранных организаций нет значений при текущих фильтрах и пороге публикаций.")
            else:
                period_order = (
                    organization_history[["PeriodStart", "Period"]]
                    .drop_duplicates()
                    .sort_values("PeriodStart")["Period"]
                    .astype(str)
                    .tolist()
                )
                selected_history["Окно"] = selected_history["Period"].astype(str)
                value_fields = [("P", "Динамика публикаций P")]
                if metric != "P":
                    value_fields.append((metric, f"Динамика показателя: {metric_title}"))
                for value_field, chart_title in value_fields:
                    field_label = "Публикации P" if value_field == "P" else metric_title
                    fig_organization_values = px.line(
                        selected_history,
                        x="Окно",
                        y=value_field,
                        color="University display",
                        markers=True,
                        category_orders={"Окно": period_order},
                        color_discrete_sequence=px.colors.qualitative.Safe,
                        labels={
                            "Окно": "Окно публикаций",
                            value_field: field_label,
                            "University display": "Университет",
                        },
                        hover_data={"P": ":,.1f"},
                    )
                    if value_field in RATE_META:
                        fig_organization_values.update_yaxes(tickformat=".1%")
                    elif value_field in AVERAGE_META:
                        fig_organization_values.update_yaxes(tickformat=".2f")
                    else:
                        fig_organization_values.update_yaxes(tickformat=",.0f")
                    fig_organization_values.update_layout(
                        height=400,
                        title=chart_title,
                        title_font_size=16,
                        hovermode="x unified",
                        margin=dict(l=15, r=10, t=55, b=35),
                        legend_title_text="",
                    )
                    st.plotly_chart(fig_organization_values, use_container_width=True)

                rank_scope = st.radio(
                    "Место показывать",
                    ["В мире", "В России"],
                    horizontal=True,
                    key="organization_rank_scope",
                )
                rank_field = "World rank" if rank_scope == "В мире" else "Russia rank"
                rank_history = selected_history.dropna(subset=[rank_field]).copy()
                if rank_history.empty:
                    st.info("Среди выбранных организаций нет российских вузов для сравнения мест в России.")
                else:
                    rank_history["Окно"] = rank_history["Period"].astype(str)
                    rank_hover = {"P": ":,.1f"}
                    if metric != "P":
                        rank_hover[metric] = ":.3%" if metric in RATE_META else ":,.2f"
                    fig_organization_rank = px.line(
                        rank_history,
                        x="Окно",
                        y=rank_field,
                        color="University display",
                        markers=True,
                        category_orders={"Окно": period_order},
                        color_discrete_sequence=px.colors.qualitative.Safe,
                        labels={
                            "Окно": "Окно публикаций",
                            rank_field: "Место (1 — первое)",
                            "University display": "Университет",
                        },
                        hover_data=rank_hover,
                    )
                    fig_organization_rank.update_yaxes(autorange="reversed")
                    fig_organization_rank.update_layout(
                        height=440,
                        title=f"Динамика мест {rank_scope.lower()} по показателю: {metric_title}",
                        title_font_size=16,
                        hovermode="x unified",
                        margin=dict(l=15, r=10, t=55, b=35),
                        legend_title_text="",
                    )
                    st.plotly_chart(fig_organization_rank, use_container_width=True)
                st.caption(
                    "Места рассчитываются заново для каждого окна среди организаций, прошедших порог P. "
                    "При одинаковом значении показателя организации делят место; по России ранжируются только российские вузы."
                )


with method_tab:
    st.subheader("Как читать показатели")
    st.markdown(
        """
        В рейтинге нет единого балла «за качество». Каждый показатель отвечает на свой вопрос, поэтому один и тот же вуз
        может быть высоко по числу публикаций и заметно ниже по их цитируемости.

        **Объём и цитируемость**

        - **P** — сколько статей и обзоров попало в базу рейтинга.
        - **P(top 1/5/10/50 %)** — число публикаций университета среди наиболее цитируемых работ в своей области и году.
          **PP(top … %)** показывает долю таких работ от всех публикаций университета. Для PP(top 10 %) ориентир — около 10 %.
        - **MNCS** сравнивает среднюю цитируемость с ожидаемым уровнем для той же области и года: 1 — примерно средний
          уровень, 2 — примерно вдвое выше. Это среднее по всем работам, поэтому оно может отличаться от доли статей в top 10 %.
        - **MCS** — среднее число обычных цитирований; оно зависит от области и возраста публикации. **TCS** и **TNCS** —
          суммарные, а не средние показатели цитирования.

        **Сотрудничество и открытый доступ**

        - Показатели сотрудничества считают публикации с соавторами из других организаций, других стран или индустрии.
          Отдельно показаны работы с близкими и очень удалёнными соавторами. Одна статья может подходить сразу под
          несколько видов сотрудничества, поэтому эти доли не складываются в 100 %.
        - **OA** — публикации, доступные открыто; **Gold, Hybrid, Green и Bronze** обозначают разные варианты такого доступа.
        """
    )
    st.subheader("Как устроены сравнения")
    st.markdown(
        """
        - В таблицах можно встретить полный и дробный подсчёт. При полном одна совместная статья целиком засчитывается
          каждому университету в списке авторов; при дробном её вклад делится между организациями. Поэтому суммы при
          полном подсчёте могут включать одну и ту же статью несколько раз. Для показателей научного влияния доступен
          дробный подсчёт; для сотрудничества, открытого доступа и авторств CWTS использует полный.
        - Окна публикаций длятся по четыре года и перекрываются на три года. Например, 2020–2023 и 2021–2024 — почти
          одни и те же публикации, поэтому их разницу не нужно трактовать как изменение за один год.
        - На вкладке стран сравниваются университеты, вошедшие в рейтинг CWTS. Доля страны там не равна её доле во всей
          мировой науке: журналы и типы публикаций в базе охвачены не полностью.
        """
    )
    st.subheader("Охват и ограничения")
    st.markdown(
        """
        - В выпуске — **1 618 университетов из 78 стран и территорий**. Последнее окно публикаций — **2021–2024**;
          до него доступны ещё 15 четырёхлетних окон, начиная с 2006–2009.
        - Рейтинг считает статьи и обзоры на английском языке из выбранных журналов Web of Science. Это не полный
          каталог научных результатов: книги, конференционные материалы и часть журналов здесь не учтены.
        - Цитирования для периода 2021–2024 учитываются до конца 2025 года; для более ранних окон действует тот же
          принцип — до конца первого года после окончания периода.
        - Для некоторых показателей CWTS показывает интервал устойчивости на уровне 95 % — диапазон, в котором оценка может
          колебаться при пересчёте публикаций. Если интервалы двух вузов пересекаются, небольшую разницу между ними
          не стоит считать статистически значимой разницей.
        - Выпуск 2026 года — последний в версии Traditional Edition. С 2027 года останется Open Edition на OpenAlex;
          данные и методика будут другими, поэтому прямое сравнение с этим рядом потребует осторожности. CWTS также
          предупреждает, что в нынешней базе нельзя надёжно выявить все публикации так называемых paper mills; их влияние
          на результаты рейтинга пока трудно оценить.
        """
    )
    st.subheader("Источники")
    st.markdown(
        """
        - [Таблица CWTS Leiden Ranking 2026](https://traditional.leidenranking.com/ranking/2026/list)
        - [Выгрузка результатов и исходный Excel-файл](https://doi.org/10.5281/zenodo.23597012)
        - [Определения индикаторов и методика CWTS](https://traditional.leidenranking.com/information/indicators)
        - [Университеты и правила их отбора](https://traditional.leidenranking.com/information/universities)
        - [Финальный выпуск Traditional Edition: комментарий CWTS](https://www.leidenmadtrics.nl/articles/the-cwts-leiden-ranking-2026-final-release-of-the-traditional-edition)
        """
    )

st.divider()
st.markdown(
    '<p class="source-note">Данные: CWTS Leiden Ranking Traditional Edition 2026, таблица результатов на Zenodo, DOI 10.5281/zenodo.23597012. '
    'Исходная выгрузка распространяется по CC BY 4.0; университетские показатели интерпретируйте вместе с контекстом и ограничениями источника.</p>',
    unsafe_allow_html=True,
)
