"""
MSBA 325 - Interactive Visualizations with Streamlit
Dataset: Foreign Direct Investment, Lebanon (1990-2022)
Source:  AUB Linked Data Portal (linked.aub.edu.lb), originally FAOSTAT
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# PAGE SETUP
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Lebanon FDI, 1990-2022",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

PRIMARY = "#065A82"    # deep blue  - inflows
SECONDARY = "#E07A5F"  # coral      - outflows
HIGHLIGHT = "#C1292E"  # red        - the selected year
MUTED = "#B9C6CD"      # grey       - everything not selected


# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "fdi.csv") -> pd.DataFrame:
    """Read the portal export and reshape it to one row per year."""
    df = pd.read_csv(path)

    # The file is long format: one row per year per flow type.
    df = df[["Year", "Item", "Value"]]
    wide = df.pivot_table(index="Year", columns="Item", values="Value").reset_index()

    # Name the two flow columns by what they contain, not by their position.
    rename = {}
    for col in wide.columns:
        name = str(col).lower()
        if "inflow" in name:
            rename[col] = "Inflows"
        elif "outflow" in name:
            rename[col] = "Outflows"
    wide = wide.rename(columns=rename)

    # Fallback in case the item labels are worded differently.
    if "Inflows" not in wide.columns or "Outflows" not in wide.columns:
        others = [c for c in wide.columns if c != "Year"]
        wide = wide.rename(columns={others[0]: "Inflows", others[1]: "Outflows"})

    wide["Year"] = wide["Year"].astype(int)
    wide["Net"] = wide["Inflows"] - wide["Outflows"]
    return wide.sort_values("Year").reset_index(drop=True)


fdi = load_data()
YEAR_MIN, YEAR_MAX = int(fdi["Year"].min()), int(fdi["Year"].max())


# ----------------------------------------------------------------------
# HEADER AND CONTEXT
# ----------------------------------------------------------------------
st.title("Can Lebanon count on foreign investment?")
st.caption(
    "Foreign Direct Investment in Lebanon, 1990-2022 - AUB Linked Data Portal "
    "(linked.aub.edu.lb), originally FAOSTAT. All figures in millions of US dollars."
)

st.markdown(
    """
Foreign Direct Investment is money that foreign companies and individuals put into a country
to own something in it: a factory, a bank, a building. **Inflows** are money arriving in Lebanon.
**Outflows** are money Lebanese investors send abroad. The gap between them is the **net position** -
whether the country was, on balance, receiving or sending capital that year.

Lebanon's 33 years here are not one continuous story. Post-war reconstruction, the boom of the 2000s
and the collapse after 2019 are effectively three different economies, so a single average across the
whole period describes none of them. Use the controls in the sidebar to look at one period at a time,
then drill into a single year.
"""
)


# ----------------------------------------------------------------------
# INTERACTION FEATURE 1: the period slider
# ----------------------------------------------------------------------
st.sidebar.header("Controls")

start_year, end_year = st.sidebar.slider(
    "1. Choose a period",
    min_value=YEAR_MIN,
    max_value=YEAR_MAX,
    value=(YEAR_MIN, YEAR_MAX),
    step=1,
    help="Everything on this page is limited to the years you pick here.",
)

window = fdi[(fdi["Year"] >= start_year) & (fdi["Year"] <= end_year)].copy()

# ----------------------------------------------------------------------
# INTERACTION FEATURE 2: the year picker, fed by feature 1
# ----------------------------------------------------------------------
years_available = window["Year"].tolist()
peak_year = int(window.loc[window["Inflows"].idxmax(), "Year"])

selected_year = st.sidebar.selectbox(
    "2. Zoom in on one year",
    options=years_available,
    index=years_available.index(peak_year),
    help="Only the years inside the period above are listed here.",
)

st.sidebar.caption(
    f"{len(years_available)} year(s) in this period. "
    "Move the slider and watch this list change - the two controls are linked."
)

row = window[window["Year"] == selected_year].iloc[0]
prev = fdi[fdi["Year"] == selected_year - 1]


# ----------------------------------------------------------------------
# THE SELECTED YEAR, IN NUMBERS
# ----------------------------------------------------------------------
st.subheader(f"{selected_year} at a glance")

c1, c2, c3 = st.columns(3)
delta = None
if not prev.empty:
    change = row["Inflows"] - prev.iloc[0]["Inflows"]
    delta = f"{change:+,.0f} vs {selected_year - 1}"

c1.metric("Inflows", f"${row['Inflows']:,.0f}M", delta)
c2.metric("Outflows", f"${row['Outflows']:,.0f}M")
c3.metric("Net position", f"${row['Net']:,.0f}M")


# ----------------------------------------------------------------------
# CHART 1: the shape of the period
# ----------------------------------------------------------------------
st.subheader(f"Inflows and outflows, {start_year}-{end_year}")

fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x=window["Year"], y=window["Inflows"], name="Inflows",
        mode="lines+markers", line=dict(color=PRIMARY, width=3), marker=dict(size=6),
        hovertemplate="%{x}<br>Inflows: $%{y:,.0f}M<extra></extra>",
    )
)
fig1.add_trace(
    go.Scatter(
        x=window["Year"], y=window["Outflows"], name="Outflows",
        mode="lines+markers", line=dict(color=SECONDARY, width=3), marker=dict(size=6),
        hovertemplate="%{x}<br>Outflows: $%{y:,.0f}M<extra></extra>",
    )
)

# Mark the year chosen with the second control, so the link is visible on the chart.
fig1.add_vline(
    x=selected_year, line_width=2, line_dash="dash", line_color=HIGHLIGHT,
    annotation_text=str(selected_year), annotation_position="top",
    annotation_font_color=HIGHLIGHT,
)

fig1.update_layout(
    template="plotly_white",
    font=dict(family="Arial", size=14),
    xaxis_title="Year",
    yaxis_title="Million USD",
    hovermode="x unified",
    legend=dict(orientation="h", y=1.12, x=0),
    margin=dict(l=60, r=30, t=50, b=50),
    height=430,
)
st.plotly_chart(fig1, width="stretch")


# ----------------------------------------------------------------------
# CHART 2: net position per year, selected year highlighted
# ----------------------------------------------------------------------
st.subheader(f"Net position per year, {start_year}-{end_year}")

colors = [HIGHLIGHT if y == selected_year else MUTED for y in window["Year"]]

fig2 = go.Figure()
fig2.add_trace(
    go.Bar(
        x=window["Year"], y=window["Net"], marker_color=colors,
        hovertemplate="%{x}<br>Net: $%{y:,.0f}M<extra></extra>",
        name="Net position",
    )
)
fig2.add_hline(y=0, line_width=1.5, line_color="#444444")
fig2.update_layout(
    template="plotly_white",
    font=dict(family="Arial", size=14),
    xaxis_title="Year",
    yaxis_title="Inflows minus outflows (million USD)",
    showlegend=False,
    margin=dict(l=60, r=30, t=50, b=50),
    height=400,
)
st.plotly_chart(fig2, width="stretch")
caption = (
    f"Every bar above the line is a year Lebanon received more than it sent. "
    f"{selected_year} is shown in red."
)
if 2021 in years_available:
    caption += (
        " Note 2021: its bar is tall because outflows were negative that year, "
        "not because inflows were strong - they had fallen to $605M."
    )
st.caption(caption)


# ----------------------------------------------------------------------
# INSIGHTS
# ----------------------------------------------------------------------
st.subheader("Two things worth noticing")

peak_value = window["Inflows"].max()
last_value = window["Inflows"].iloc[-1]
first_value = window["Inflows"].iloc[0]
positive_years = int((window["Net"] > 0).sum())

col_a, col_b = st.columns(2)

with col_a:
    st.markdown(
        f"""
**1. The money arrived in one window, and that window has closed.**

Almost nothing came in before 1996 - under \\$100M a year. Inflows jumped to
**\\$1.80B in 1997** as post-war reconstruction began and climbed to a peak of
**\\$4.38B in 2009**. More than half of all the FDI Lebanon has ever received arrived
in the fourteen years between 1997 and 2010. Through the 2010s inflows drifted down with
occasional rebounds, then fell away after 2019: **\\$458M in 2022**, roughly a tenth of
the peak and back to late-1990s levels. In the period selected, the high point is
**{peak_year}** at \\${peak_value:,.0f}M.
"""
    )

with col_b:
    st.markdown(
        f"""
**2. Outflows are not a footnote - and in 2021 they ran backwards.**

Money leaving matters more than it first appears: since 2003, outflows have run between
13% and 74% of inflows, and in 2013 they reached **\\$1.98B against \\$2.66B coming in**,
nearly closing the gap. Then 2021 does something odd - outflows are **negative,
-\\$1.37B**, meaning Lebanese investors pulled back more from abroad than they sent out.
That makes 2021's net position look healthy at \\$1.97B even though inflows had already
collapsed to \\$605M. The net figure alone can flatter a bad year; both lines have to be
read together, which is why this page shows them separately.
"""
    )


# ----------------------------------------------------------------------
# DESIGN JUSTIFICATIONS
# ----------------------------------------------------------------------
st.subheader("Why these two controls")

with st.expander("Feature 1 - the period slider"):
    st.markdown(
        """
**The question it answers:** *What did FDI look like during one particular era?*

Lebanon's 33 years are not one continuous period. Reconstruction, the 2000s boom and the
post-2019 collapse behave like different economies, so any figure averaged across all of them
describes none of them. The slider lets a reader isolate the era they actually care about.

**Why a slider rather than the alternative.** I considered a multiselect listing every year.
I rejected it because years are ordered and continuous: a multiselect would let someone pick
1993 and 2018 with nothing in between, and a line drawn across that gap would be a lie. A
range slider can only ever produce an unbroken window, which is the only shape that makes
sense on a time axis. I also considered a decade dropdown, but the interesting boundaries in
this data (1997, 2009, 2019) fall inside decades, not between them.

**The course concept.** This is decluttering and focusing attention. Drawing all 33 years at
once forces the reader to do the filtering in their own head, and the flat near-zero stretch
from 1990 to 1996 squashes the rest of the chart. Removing years the reader did not ask for
gives the remaining ones room to be read.
"""
    )

with st.expander("Feature 2 - the year picker (linked to the slider)"):
    st.markdown(
        """
**The question it answers:** *That spike, that drop - what were the actual numbers that year?*

The first chart shows shape; it does not give values. Once a reader notices something, the next
question is always about one specific year. This control answers it, and marks that year on both
charts at once so the reader never loses their place.

**How it is linked.** The dropdown is populated from the slider's output, not from the full
dataset. Narrow the period to 2005-2010 and only those six years are offered. The reader drills
down inside a period rather than filtering two unrelated things, and it is impossible to select
a year that is not on screen.

**Why a dropdown rather than the alternative.** I considered a second slider. After the period
filter there are often fewer than ten valid years, and a dropdown shows them as an explicit list -
seeing that list shrink is what tells the reader the two controls are connected. A second slider
would have looked like a duplicate of the first and hidden the relationship.

**The course concept.** This is context. A figure like \\$4.38B means nothing on its own; it only
means something read against the years around it. Rather than pulling the year out into a separate
table, the selection stays anchored in both charts, so the number and its surroundings are read
together.
"""
    )


# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------
with st.expander("See the underlying data"):
    st.dataframe(window, width="stretch", hide_index=True)
    st.caption(
        "Foreign Direct Investment, Lebanon. AUB Linked Data Portal (linked.aub.edu.lb), "
        "originally FAOSTAT. Values in millions of US dollars."
    )
