from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide",
)

sns.set_theme(style="whitegrid")


def categorize_time_window(hr: int) -> str:
    if 6 <= hr <= 9:
        return "Morning Commute (06-09)"
    if 10 <= hr <= 15:
        return "Midday / Leisure (10-15)"
    if 16 <= hr <= 19:
        return "Evening Commute (16-19)"
    return "Night / Off-Peak (20-05)"


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    base_dir = Path(__file__).resolve().parent
    day_df = pd.read_csv(base_dir / "day_clean.csv")
    hour_df = pd.read_csv(base_dir / "hour_clean.csv")

    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    hour_df["time_cluster"] = hour_df["hr"].apply(categorize_time_window)
    return day_df, hour_df


def render_sidebar(day_df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, list[str], list[str]]:
    st.sidebar.header("Filter Analisis")

    min_date = day_df["dteday"].min().date()
    max_date = day_df["dteday"].max().date()

    date_range = st.sidebar.date_input(
        label="Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    elif isinstance(date_range, tuple) and len(date_range) == 1:
        start_date = end_date = pd.to_datetime(date_range[0])
    else:
        start_date = end_date = pd.to_datetime(date_range)

    season_options = ["Spring", "Summer", "Fall", "Winter"]
    selected_seasons = st.sidebar.multiselect(
        label="Musim",
        options=season_options,
        default=season_options,
    )

    daytype_options = ["Working Day", "Weekend / Holiday"]
    selected_daytypes = st.sidebar.multiselect(
        label="Tipe Hari",
        options=daytype_options,
        default=daytype_options,
    )

    return start_date, end_date, selected_seasons, selected_daytypes


def main() -> None:
    day_df, hour_df = load_data()
    start_date, end_date, selected_seasons, selected_daytypes = render_sidebar(day_df)

    filtered_day = day_df[
        (day_df["dteday"] >= start_date)
        & (day_df["dteday"] <= end_date)
        & (day_df["season_label"].isin(selected_seasons))
        & (day_df["day_type"].isin(selected_daytypes))
    ]

    filtered_hour = hour_df[
        (hour_df["dteday"] >= start_date)
        & (hour_df["dteday"] <= end_date)
        & (hour_df["season_label"].isin(selected_seasons))
        & (hour_df["day_type"].isin(selected_daytypes))
    ]

    st.title("🚲 Bike Sharing Analytics Dashboard (2011–2012)")
    st.caption("Analisis performa penyewaan sepeda berdasarkan tren waktu, musim, cuaca, dan segmen pengguna.")

    if filtered_day.empty or filtered_hour.empty:
        st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan sesuaikan filter di sidebar.")
        st.stop()

    total_rentals = int(filtered_day["cnt"].sum())
    avg_daily = float(filtered_day["cnt"].mean())
    total_registered = int(filtered_day["registered"].sum())
    total_casual = int(filtered_day["casual"].sum())

    reg_pct = (total_registered / total_rentals * 100) if total_rentals else 0.0
    cas_pct = (total_casual / total_rentals * 100) if total_rentals else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Penyewaan", f"{total_rentals:,}")
    col2.metric("Rata-Rata / Hari", f"{avg_daily:,.0f}")
    col3.metric("Pengguna Registered", f"{total_registered:,}", f"{reg_pct:.2f}%")
    col4.metric("Pengguna Casual", f"{total_casual:,}", f"{cas_pct:.2f}%")

    st.divider()

    st.subheader("1. Tren Bulanan, Musim, dan Kondisi Cuaca")

    monthly_trend = (
        filtered_day.groupby(["year", "mnth"], as_index=False)["cnt"]
        .sum()
        .sort_values(["year", "mnth"])
    )
    monthly_trend["year_month"] = (
        monthly_trend["year"].astype(str) + "-" + monthly_trend["mnth"].astype(str).str.zfill(2)
    )

    fig_trend, ax_trend = plt.subplots(figsize=(14, 4.5))
    sns.lineplot(
        data=monthly_trend,
        x="year_month",
        y="cnt",
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        ax=ax_trend,
    )
    ax_trend.set_title("Tren Jumlah Penyewaan Sepeda Bulanan", fontsize=13, fontweight="bold")
    ax_trend.set_xlabel("Periode (Tahun-Bulan)")
    ax_trend.set_ylabel("Total Penyewaan")
    ax_trend.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    st.pyplot(fig_trend)

    col_left, col_right = st.columns(2)

    with col_left:
        season_order = ["Fall", "Summer", "Winter", "Spring"]
        available_seasons = [s for s in season_order if s in filtered_day["season_label"].unique()]
        season_avg = (
            filtered_day.groupby("season_label")["cnt"]
            .mean()
            .reindex(available_seasons)
            .reset_index()
        )
        top_season = season_avg.loc[season_avg["cnt"].idxmax(), "season_label"]
        palette_season = ["#1f77b4" if s == top_season else "#b0c4de" for s in available_seasons]

        fig_season, ax_season = plt.subplots(figsize=(7, 4.5))
        sns.barplot(
            data=season_avg,
            x="season_label",
            y="cnt",
            hue="season_label",
            palette=palette_season,
            legend=False,
            ax=ax_season,
        )
        ax_season.set_title("Rata-Rata Penyewaan Harian per Musim", fontsize=12, fontweight="bold")
        ax_season.set_xlabel("Musim")
        ax_season.set_ylabel("Rata-Rata Penyewaan / Hari")
        for p in ax_season.patches:
            if p.get_height() > 0:
                ax_season.annotate(
                    f"{p.get_height():,.0f}",
                    (p.get_x() + p.get_width() / 2.0, p.get_height()),
                    ha="center",
                    va="bottom",
                    fontsize=9.5,
                    fontweight="bold",
                )
        plt.tight_layout()
        st.pyplot(fig_season)

    with col_right:
        weather_order = ["Clear / Partly Cloudy", "Mist / Cloudy", "Light Snow / Rain", "Heavy Rain / Ice"]
        available_weather = [w for w in weather_order if w in filtered_day["weather_label"].unique()]
        weather_avg = (
            filtered_day.groupby("weather_label")["cnt"]
            .mean()
            .reindex(available_weather)
            .reset_index()
        )
        top_weather = weather_avg.loc[weather_avg["cnt"].idxmax(), "weather_label"]
        palette_weather = ["#2ca02c" if w == top_weather else "#b8d8be" for w in available_weather]

        fig_weather, ax_weather = plt.subplots(figsize=(7, 4.5))
        sns.barplot(
            data=weather_avg,
            x="weather_label",
            y="cnt",
            hue="weather_label",
            palette=palette_weather,
            legend=False,
            ax=ax_weather,
        )
        ax_weather.set_title("Rata-Rata Penyewaan Harian per Kondisi Cuaca", fontsize=12, fontweight="bold")
        ax_weather.set_xlabel("Kondisi Cuaca")
        ax_weather.set_ylabel("Rata-Rata Penyewaan / Hari")
        for p in ax_weather.patches:
            if p.get_height() > 0:
                ax_weather.annotate(
                    f"{p.get_height():,.0f}",
                    (p.get_x() + p.get_width() / 2.0, p.get_height()),
                    ha="center",
                    va="bottom",
                    fontsize=9.5,
                    fontweight="bold",
                )
        plt.tight_layout()
        st.pyplot(fig_weather)

    st.divider()

    st.subheader("2. Pola Penyewaan per Jam & Segmen Pengguna")

    col_hr, col_seg = st.columns(2)

    with col_hr:
        hourly_pattern = (
            filtered_hour.groupby(["day_type", "hr"], as_index=False)[["cnt", "casual", "registered"]]
            .mean()
        )
        fig_hr, ax_hr = plt.subplots(figsize=(7.5, 4.5))
        sns.lineplot(
            data=hourly_pattern,
            x="hr",
            y="cnt",
            hue="day_type",
            marker="o",
            linewidth=2.2,
            palette={"Working Day": "#1f77b4", "Weekend / Holiday": "#ff7f0e"},
            ax=ax_hr,
        )
        ax_hr.set_title("Pola Rata-Rata Penyewaan per Jam", fontsize=12, fontweight="bold")
        ax_hr.set_xlabel("Jam (00:00 - 23:00)")
        ax_hr.set_ylabel("Rata-Rata Penyewaan / Jam")
        ax_hr.set_xticks(range(0, 24, 2))
        ax_hr.legend(title="Tipe Hari")
        plt.tight_layout()
        st.pyplot(fig_hr)

    with col_seg:
        segment_daytype = (
            filtered_day.groupby("day_type", as_index=False)[["casual", "registered"]]
            .mean()
            .melt(id_vars="day_type", var_name="user_type", value_name="avg_rentals")
        )
        fig_seg, ax_seg = plt.subplots(figsize=(7.5, 4.5))
        sns.barplot(
            data=segment_daytype,
            x="day_type",
            y="avg_rentals",
            hue="user_type",
            palette={"casual": "#ff7f0e", "registered": "#1f77b4"},
            ax=ax_seg,
        )
        ax_seg.set_title("Rata-Rata Penyewaan Harian: Casual vs Registered", fontsize=12, fontweight="bold")
        ax_seg.set_xlabel("Tipe Hari")
        ax_seg.set_ylabel("Rata-Rata Penyewaan / Hari")
        ax_seg.legend(title="Tipe Pengguna")
        for p in ax_seg.patches:
            if p.get_height() > 0:
                ax_seg.annotate(
                    f"{p.get_height():,.0f}",
                    (p.get_x() + p.get_width() / 2.0, p.get_height()),
                    ha="center",
                    va="bottom",
                    fontsize=9.5,
                    fontweight="bold",
                )
        plt.tight_layout()
        st.pyplot(fig_seg)

    st.divider()

    st.subheader("3. Segmentasi Klaster Waktu Operasional")

    cluster_summary = (
        filtered_hour.groupby(["day_type", "time_cluster"], as_index=False)["cnt"]
        .mean()
    )
    order_cluster = [
        "Morning Commute (06-09)",
        "Midday / Leisure (10-15)",
        "Evening Commute (16-19)",
        "Night / Off-Peak (20-05)",
    ]

    fig_cluster, ax_cluster = plt.subplots(figsize=(14, 4.5))
    sns.barplot(
        data=cluster_summary,
        x="time_cluster",
        y="cnt",
        hue="day_type",
        order=order_cluster,
        palette={"Working Day": "#1f77b4", "Weekend / Holiday": "#ff7f0e"},
        ax=ax_cluster,
    )
    ax_cluster.set_title("Rata-Rata Penyewaan per Jam Berdasarkan Klaster Waktu", fontsize=13, fontweight="bold")
    ax_cluster.set_xlabel("Klaster Waktu")
    ax_cluster.set_ylabel("Rata-Rata Penyewaan / Jam")
    ax_cluster.legend(title="Tipe Hari")
    for p in ax_cluster.patches:
        if p.get_height() > 0:
            ax_cluster.annotate(
                f"{p.get_height():,.0f}",
                (p.get_x() + p.get_width() / 2.0, p.get_height()),
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
            )
    plt.tight_layout()
    st.pyplot(fig_cluster)

    st.caption("Muhammad Anbiya Fatah — Proyek Analisis Data: Bike Sharing Dataset")


if __name__ == "__main__":
    main()