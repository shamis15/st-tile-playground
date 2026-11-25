"""Playground for exploring st.tile looks on dashboard-style layouts."""

import numpy as np
import pandas as pd

import streamlit as st

st.set_page_config(page_title="st.tile playground", layout="wide")

rng = np.random.default_rng(7)
months = pd.date_range("2025-01-01", periods=12, freq="MS")
mrr = pd.DataFrame(
    {
        "Starter": np.cumsum(rng.uniform(8, 14, 12)) + 40,
        "Team": np.cumsum(rng.uniform(10, 20, 12)) + 80,
        "Enterprise": np.cumsum(rng.uniform(15, 30, 12)) + 120,
    },
    index=months,
)
mrr_share = mrr.div(mrr.sum(axis=1), axis=0) * 100
regions = pd.DataFrame(
    {"Revenue": [412, 318, 274, 141, 96]},
    index=["North America", "Europe", "APAC", "LATAM", "MEA"],
)
accounts = pd.DataFrame(
    {
        "Account": [f"Acme {i}" for i in range(1, 16)],
        "Plan": rng.choice(["Starter", "Team", "Enterprise"], 15),
        "Seats": rng.integers(5, 400, 15),
        "Renewal": pd.date_range("2026-11-20", periods=15, freq="5D"),
        "Health": rng.choice(["Healthy", "At risk", "Churning"], 15),
        "NPS": rng.integers(12, 82, 15),
    }
)
funnel = pd.Series(
    {"Visit": 8200, "Signup": 1940, "Trial": 740, "Paid": 312}, dtype=float
)
pipeline = pd.DataFrame(
    {
        "Account": [f"Acme {i}" for i in range(1, 9)],
        "Stage": rng.choice(["Discovery", "Proposal", "Negotiation", "Closed won"], 8),
        "Amount": rng.integers(12, 180, 8) * 1000,
        "Close": pd.date_range("2026-12-01", periods=8, freq="10D"),
        "Owner": rng.choice(["Ana", "Ben", "Cara"], 8),
    }
)
hourly = pd.DataFrame(
    rng.integers(8, 48, size=(7, 12)),
    index=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    columns=[f"{h:02d}" for h in range(8, 20)],
)

with st.sidebar:
    surface_tab, details_tab, examples_tab = st.tabs(["Surface", "Details", "Examples"])

    with surface_tab:
        variant = st.radio(
            "Header treatment",
            ["default", "divided", "accent"],
            index=1,
            captions=[
                "Header sits on the body",
                "Divider under the header",
                "Primary bar on top edge",
            ],
        )
        surface = st.radio(
            "Surface",
            ["Outlined", "Filled + outline", "Filled, no outline"],
            index=1,
            captions=[
                "Border only",
                "Fill and border",
                "Fill only",
            ],
        )
        elevated = st.toggle(
            "Elevated",
            value=False,
            help="Adds a light drop shadow. Combines with any surface.",
        )
        fill = st.color_picker("Tile background", "#ffffff")
        page_bg = st.color_picker(
            "Main background",
            "#171614" if st.context.theme.type == "dark" else "#ffffff",
        )

        def _is_light(hex_color: str) -> bool:
            # Relative luminance above ~0.18 contrasts better with dark text.
            channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
            lin = [
                c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                for c in channels
            ]
            return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2] > 0.179

        _dark_ink, _light_ink = "#1a1a1a", "#fafafa"
        text_mode = st.radio(
            "Text color",
            ["Auto", "Custom"],
            horizontal=True,
            captions=["Contrast with each background", "Pick tile and page text"],
            key="tile-text-mode",
        )
        _text_tags = "p, span, label, li, h1, h2, h3, h4, h5, h6"
        # Skip badges, metric deltas and buttons so colored fills keep readable text.
        _tile_text_rule = f"""
              [data-testid="stTile"] :is({_text_tags}):not(
                .stMarkdownBadge, .stMarkdownBadge *, [data-testid="stBadge"] *,
                [data-testid="stMetricDelta"] *, button *, [data-baseweb] *
              ) {{ color: %s !important; }}
        """
        _main_text_rule = f"""
              [data-testid="stMain"] :is({_text_tags}):not(
                [data-testid="stTile"] *, button *, [data-baseweb] *
              ) {{ color: %s !important; }}
        """
        text_css = ""
        page_is_light = _is_light(page_bg)
        if text_mode == "Custom":
            # Defaults follow the backgrounds, so changing a background resets
            # the picker to a readable color.
            tile_backdrop = fill if surface != "Outlined" else page_bg
            tile_text = st.color_picker(
                "Tile text", _dark_ink if _is_light(tile_backdrop) else _light_ink
            )
            main_text = st.color_picker(
                "Main text", _dark_ink if page_is_light else _light_ink
            )
            text_css = _tile_text_rule % tile_text + _main_text_rule % main_text
        elif page_is_light == (st.context.theme.type == "dark"):
            # The page background fights the theme's own text color; tiles
            # already pick their text from their fill.
            text_css = _main_text_rule % (_dark_ink if page_is_light else _light_ink)
        use_echarts = st.toggle("Use ECharts", value=False)
        tile_shadow = (
            """
              [data-testid="stTile"] {
                filter: drop-shadow(0 1px 2px rgba(15, 15, 15, 0.07))
                  drop-shadow(0 3px 8px rgba(15, 15, 15, 0.10));
              }
            """
            if elevated
            else ""
        )
        st.markdown(
            f"""
            <style>
              .stApp, [data-testid="stHeader"], [data-testid="stMain"],
              [data-testid="stBottomBlockContainer"] {{
                background-color: {page_bg} !important;
              }}
              {tile_shadow}
              {text_css}
            </style>
            """,
            unsafe_allow_html=True,
        )

    with details_tab:
        widget_size = st.radio(
            "Widget size",
            ["28px", "24px", "40px"],
            index=0,
            horizontal=True,
            captions=["1.75rem condensed", "1.5rem condensed", "Default"],
            key="tile-widget-size",
            help="Condensed controls inside tiles. Default is the usual 40px widgets.",
        )
        show_icons = st.toggle("Icons", value=True)
        show_help = st.toggle("Help tooltip", value=True)
        show_captions = st.toggle("Captions / subtitles", value=True)
        show_actions = st.toggle("Header actions", value=True)
        show_live_footer = st.toggle("Live footer badge", value=True)
        section_gap = st.radio(
            "Gap between header, body, footer",
            ["8px", "16px"],
            index=0,
            horizontal=True,
            key="tile-section-gap",
        )
        perimeter_padding = st.radio(
            "Perimeter padding",
            ["16px", "24px"],
            index=0,
            horizontal=True,
            key="tile-perimeter-padding",
        )
        kebab_style = st.radio(
            "Kebab",
            ["none", "more_horiz", "more_vert"],
            index=2,
            captions=["Off", "Horizontal dots", "Vertical dots"],
            disabled=not show_actions,
        )

    with examples_tab:
        example_page = st.radio(
            "Show in main area",
            [
                "Playground",
                "Advanced dashboard",
                "Apps that compute",
                "Workflow",
                "Why tiles",
            ],
            captions=[
                "Dashboard + widget gallery",
                "Nimbus BI",
                "Cairn Demand lab",
                "Cairn Reorder desk",
                "What this unlocks",
            ],
        )

    st.markdown(
        f"""
        <style>
          html {{
            --st-tile-controls: {"1.75rem" if widget_size == "28px" else "1.5rem" if widget_size == "24px" else "default"};
          }}
          [data-testid="stTile"] {{
            gap: {"1rem" if section_gap == "16px" else "0.5rem"} !important;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

border = surface in ("Outlined", "Filled + outline")
filled = surface in ("Filled + outline", "Filled, no outline")
background = fill if filled else False
common = {
    "border": border,
    "background": background,
    "variant": variant,
}

# 24px inset; subtract the border so the inner content lines up with 16px tiles.
_tile_pad = "calc(1.5rem - 1px)" if border else ("1.5rem" if filled else "0")
_tile_pad_css = (
    f"""
      [data-testid="stTile"] {{
        padding: {_tile_pad} !important;
      }}
    """
    if perimeter_padding == "24px" and _tile_pad != "0"
    else ""
)
_tile_divided_css = (
    f"""
      [data-testid="stTileHeader"],
      [data-testid="stTileFooter"] {{
        margin-inline: calc(-1 * {_tile_pad}) !important;
        padding-inline: {_tile_pad} !important;
      }}
    """
    if perimeter_padding == "24px" and variant == "divided" and _tile_pad != "0"
    else ""
)
st.markdown(
    f"<style>{_tile_pad_css}{_tile_divided_css}</style>",
    unsafe_allow_html=True,
)


def cap(text: str) -> str | None:
    return text if show_captions else None


def ico(icon: str) -> str | None:
    return icon if show_icons else None


def tip(text: str) -> str | None:
    return text if show_help else None


def _month_labels(index) -> list[str]:
    return [d.strftime("%b") if d.month != 1 else str(d.year) for d in index]


def area_chart(df: pd.DataFrame, *, height: int) -> None:
    if not use_echarts:
        st.area_chart(df, height=height)
        return
    st.echarts_chart(
        {
            "tooltip": {"trigger": "axis"},
            "legend": {},
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": _month_labels(df.index),
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "name": name,
                    "type": "line",
                    "stack": "total",
                    "areaStyle": {},
                    "showSymbol": False,
                    "data": [round(float(v), 1) for v in df[name].tolist()],
                }
                for name in df.columns
            ],
        },
        height=height,
    )


def bar_chart(
    data: pd.Series | pd.DataFrame,
    *,
    height: int,
    horizontal: bool = False,
) -> None:
    series = data.iloc[:, 0] if isinstance(data, pd.DataFrame) else data
    labels = [str(v) for v in series.index]
    values = [round(float(v), 1) for v in series.tolist()]
    if not use_echarts:
        st.bar_chart(data, horizontal=horizontal, height=height)
        return
    if horizontal:
        spec = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": {"type": "value"},
            "yAxis": {"type": "category", "data": labels, "inverse": True},
            "series": [{"type": "bar", "data": values}],
        }
    else:
        spec = {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": {"type": "category", "data": labels},
            "yAxis": {"type": "value"},
            "series": [{"type": "bar", "data": values}],
        }
    st.echarts_chart(spec, height=height)


def line_chart(data: pd.Series, *, height: int) -> None:
    if not use_echarts:
        st.line_chart(data, height=height)
        return
    st.echarts_chart(
        {
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": _month_labels(data.index),
            },
            "yAxis": {"type": "value"},
            "series": [
                {
                    "type": "line",
                    "showSymbol": False,
                    "data": [round(float(v), 1) for v in data.tolist()],
                }
            ],
        },
        height=height,
    )


def kebab(container, key: str) -> None:
    if not show_actions or kebab_style == "none":
        return
    # The icon is the label, with no `icon=` argument, so the chevron is hidden.
    container.header.menu_button(
        f":material/{kebab_style}:",
        ["Export", "Open report", "Copy link"],
        type="tertiary",
        key=key,
    )


def live(container) -> None:
    if not show_live_footer:
        return
    container.footer.badge("Live", icon=":material/fiber_manual_record:", color="green")


st.title("st.tile playground")
st.caption("Use the sidebar to switch looks. Open Examples to swap the page.")

if example_page == "Playground":
    dash_tab, widgets_tab = st.tabs(["Dashboard", "Widgets"])

    with dash_tab:
        st.subheader("Revenue dashboard")
        k1, k2, k3, k4 = st.columns(4)
        for col, (name, value, delta) in zip(
            (k1, k2, k3, k4),
            [
                ("ARR", "$4.2M", "+8%"),
                ("Net retention", "112%", "+2pt"),
                ("Active accounts", "1,284", "+46"),
                ("Churn", "1.9%", "-0.3pt"),
            ],
            strict=True,
        ):
            t = col.tile(
                name,
                icon=ico(":material/monitoring:"),
                help=tip(f"{name} for the selected period."),
                **common,
            )
            # KPI tiles skip the menu: in four narrow columns it wraps onto its
            # own row and leaves empty space under the title.
            live(t)
            t.metric(name, value, delta, label_visibility="collapsed")

        left, right = st.columns([3, 2])
        with left.tile(
            "MRR by plan",
            caption=cap("Monthly recurring revenue in $K"),
            icon=ico(":material/stacked_line_chart:"),
            help=tip("Sum of active subscriptions at month end."),
            **common,
        ) as tile:
            view = "$"
            if show_actions:
                view = tile.actions.segmented_control(
                    "View", ["$", "%"], default="$", label_visibility="collapsed"
                )
            kebab(tile, "mrr-menu")
            live(tile)
            area_chart(mrr if view == "$" else mrr_share, height=280)

        with right.tile(
            "Revenue by region",
            caption=cap("Last 12 months, $K"),
            icon=ico(":material/public:"),
            help=tip("Revenue by sales region for the last 12 months."),
            **common,
        ) as tile:
            kebab(tile, "region-menu")
            live(tile)
            sel_col, btn_col = st.columns([3, 1], vertical_alignment="bottom")
            sel_col.selectbox(
                "Period",
                ["Last 12 months", "Last 6 months"],
                key="dash-period",
            )
            btn_col.button("Apply", width="stretch", key="dash-apply")
            bar_chart(regions, horizontal=True, height=220)

        left, right = st.columns([2, 1])
        with left.tile(
            "Upcoming renewals",
            caption=cap("Next 90 days, soonest first"),
            icon=ico(":material/event_repeat:"),
            help=tip("Accounts renewing in the next 90 days."),
            **common,
        ) as tile:
            show_risky = False
            if show_actions:
                tile.actions.badge(f"{len(accounts)} accounts", color="gray")
                show_risky = tile.actions.toggle("At risk only", key="dash-risky")
            kebab(tile, "renewals-menu")
            data = accounts[accounts["Health"] != "Healthy"] if show_risky else accounts
            st.dataframe(data, hide_index=True, height=300)

        with right.tile(
            "Plan mix",
            caption=cap(
                "Share of seats by plan. This caption is intentionally long so you can "
                "see how it clamps to two lines in a narrow tile."
            ),
            icon=ico(":material/donut_large:"),
            help=tip("Seat count grouped by subscription plan."),
            **common,
        ) as tile:
            kebab(tile, "plan-mix-menu")
            live(tile)
            mix = accounts.groupby("Plan")["Seats"].sum()
            bar_chart(mix, height=230)

        left, right = st.columns([3, 2])
        with left.tile(
            "Conversion funnel",
            caption=cap("Visit to paid, with channel overlay"),
            icon=ico(":material/filter_alt:"),
            **common,
        ) as tile:
            channel = "All"
            if show_actions:
                channel = tile.actions.pills(
                    "Channel",
                    ["All", "Self-serve", "Sales"],
                    default="All",
                    label_visibility="collapsed",
                    key="dash-funnel-channel",
                )
            kebab(tile, "funnel-menu")
            live(tile)
            scale = (
                1.0 if channel == "All" else 0.62 if channel == "Self-serve" else 0.38
            )
            bar_chart(funnel * scale, horizontal=True, height=240)

        with right.tile(
            "Forecast vs actual",
            caption=cap("Line chart with a horizon slider"),
            icon=ico(":material/ssid_chart:"),
            **common,
        ) as tile:
            kebab(tile, "forecast-menu")
            live(tile)
            horizon = st.slider("Weeks shown", 8, 26, 16, key="dash-horizon")
            weeks = pd.date_range("2026-01-05", periods=26, freq="W")[:horizon]
            actual = np.cumsum(rng.uniform(8, 14, horizon)) + 40
            forecast_vals = actual * rng.uniform(0.96, 1.08, horizon)
            st.line_chart(
                pd.DataFrame(
                    {"Actual": actual, "Forecast": forecast_vals}, index=weeks
                ),
                height=220,
            )

        left, right = st.columns([2, 3])
        with left.tile(
            "Seats vs NPS",
            caption=cap("Scatter of accounts"),
            icon=ico(":material/scatter_plot:"),
            **common,
        ) as tile:
            kebab(tile, "scatter-menu")
            live(tile)
            plan_filter = st.multiselect(
                "Plan",
                ["Starter", "Team", "Enterprise"],
                default=["Starter", "Team", "Enterprise"],
                key="dash-scatter-plan",
            )
            scatter = accounts[accounts["Plan"].isin(plan_filter)]
            st.scatter_chart(scatter, x="Seats", y="NPS", color="Plan", height=240)

        with right.tile(
            "Pipeline",
            caption=cap("Editable opportunities"),
            icon=ico(":material/handshake:"),
            **common,
        ) as tile:
            if show_actions:
                tile.actions.segmented_control(
                    "Stage",
                    ["All", "Open", "Won"],
                    default="All",
                    label_visibility="collapsed",
                    key="dash-pipe-view",
                )
            kebab(tile, "pipeline-menu")
            st.data_editor(
                pipeline,
                hide_index=True,
                height=260,
                disabled=["Account"],
                column_config={
                    "Amount": st.column_config.NumberColumn("Amount", format="$%d"),
                    "Stage": st.column_config.SelectboxColumn(
                        "Stage",
                        options=[
                            "Discovery",
                            "Proposal",
                            "Negotiation",
                            "Closed won",
                        ],
                    ),
                    "Close": st.column_config.DateColumn("Close"),
                },
                key="dash-pipeline-editor",
            )

        with st.tile(
            "When customers use the product",
            caption=cap("Sessions by weekday and hour"),
            icon=ico(":material/schedule:"),
            **common,
        ) as tile:
            kebab(tile, "usage-menu")
            live(tile)
            day = st.radio(
                "Day",
                list(hourly.index),
                horizontal=True,
                key="dash-usage-day",
            )
            st.bar_chart(hourly.loc[day], height=200)
            st.dataframe(hourly, height=180)

        st.subheader("Edge cases")
        e1, e2, e3 = st.columns(3)
        with e1.tile(
            "A very long tile label that should truncate with an ellipsis",
            caption=cap("Fixed height of 260px; the body scrolls"),
            help=tip("Long labels truncate. Fixed-height bodies scroll."),
            height=260,
            **common,
        ) as tile:
            if show_actions:
                tile.actions.pills(
                    "Range",
                    ["7d", "30d", "90d"],
                    default="30d",
                    label_visibility="collapsed",
                    key="dash-range",
                )
            kebab(tile, "edge-long-menu")
            for i in range(8):
                st.write(f"Row {i + 1}: some scrolling content")

        with e2.tile(
            "Header only",
            caption=cap("No body content"),
            help=tip("A tile with no children."),
            **common,
        ) as tile:
            if show_actions:
                tile.actions.button(
                    "Refresh",
                    icon=":material/refresh:",
                    type="tertiary",
                    key="dash-refresh",
                )
            kebab(tile, "edge-header-menu")

        with e3.tile(
            "Nested tile",
            caption=cap("A filled tile inside a tile"),
            help=tip("Nesting is allowed."),
            **common,
        ):
            with st.tile("Inner", background=True, border=False):
                line_chart(mrr["Team"], height=140)

    with widgets_tab:
        st.caption(
            "One tile per widget family, so you can compare condensed vs default sizes."
        )

        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1.tile(
            "Buttons",
            caption=cap("Primary, secondary, tertiary, download"),
            icon=ico(":material/smart_button:"),
            **common,
        ) as tile:
            kebab(tile, "w-buttons-menu")
            a, b, c = st.columns(3)
            a.button("Save", type="primary", key="w-btn-primary")
            b.button("Cancel", key="w-btn-secondary")
            c.button(
                "More",
                type="tertiary",
                icon=":material/more_horiz:",
                key="w-btn-tertiary",
            )
            st.download_button(
                "Export CSV", "a,b\n1,2\n", "sample.csv", key="w-download"
            )

        with r1c2.tile(
            "Choices",
            caption=cap("Checkbox, toggle, radio"),
            icon=ico(":material/checklist:"),
            **common,
        ) as tile:
            kebab(tile, "w-choices-menu")
            st.checkbox("Include churned", key="w-check")
            st.toggle("Live refresh", value=True, key="w-toggle")
            st.radio("Grain", ["Day", "Week", "Month"], horizontal=True, key="w-radio")

        with r1c3.tile(
            "Selects",
            caption=cap("Selectbox, multiselect, pills"),
            icon=ico(":material/arrow_drop_down:"),
            **common,
        ) as tile:
            kebab(tile, "w-selects-menu")
            st.selectbox("Region", ["All", *regions.index.tolist()], key="w-select")
            st.multiselect(
                "Plan",
                ["Starter", "Team", "Enterprise"],
                default=["Team"],
                key="w-multi",
            )
            st.pills(
                "Channels",
                ["Email", "In-app", "Ads"],
                selection_mode="multi",
                key="w-pills",
            )

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1.tile(
            "Sliders",
            caption=cap("Numeric, range, select slider"),
            icon=ico(":material/tune:"),
            **common,
        ) as tile:
            kebab(tile, "w-sliders-menu")
            st.slider("Confidence", 0, 100, 72, key="w-slider")
            st.slider("Seat range", 0, 400, (40, 220), key="w-range")
            st.select_slider(
                "Priority",
                ["P0", "P1", "P2", "P3"],
                value="P1",
                key="w-select-slider",
            )

        with r2c2.tile(
            "Text & numbers",
            caption=cap("Text, number, text area"),
            icon=ico(":material/edit:"),
            **common,
        ) as tile:
            kebab(tile, "w-text-menu")
            st.text_input("Account", placeholder="Acme 12", key="w-text")
            st.number_input("Seats", min_value=1, value=24, key="w-number")
            st.text_area(
                "Note", placeholder="Why this change?", height=80, key="w-area"
            )

        with r2c3.tile(
            "Dates & time",
            caption=cap("Date, range, time"),
            icon=ico(":material/calendar_month:"),
            **common,
        ) as tile:
            kebab(tile, "w-dates-menu")
            st.date_input("As of", value=pd.Timestamp("2026-11-16"), key="w-date")
            st.date_input(
                "Window",
                value=(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-11-16")),
                key="w-daterange",
            )
            st.time_input("Cutoff", value=None, key="w-time")

        r3c1, r3c2, r3c3 = st.columns(3)
        with r3c1.tile(
            "Media & color",
            caption=cap("Uploader and color picker"),
            icon=ico(":material/attach_file:"),
            **common,
        ) as tile:
            kebab(tile, "w-media-menu")
            st.file_uploader("CSV or screenshot", type=["csv", "png"], key="w-upload")
            st.color_picker("Accent", "#ff4b4b", key="w-color")

        with r3c2.tile(
            "Feedback & status",
            caption=cap("Thumbs, stars, progress"),
            icon=ico(":material/rate_review:"),
            **common,
        ) as tile:
            kebab(tile, "w-feedback-menu")
            st.feedback("thumbs", key="w-thumbs")
            st.feedback("stars", key="w-stars")
            st.progress(0.64, text="Backfill 64%")
            with st.status("Refreshing warehouse", expanded=False):
                st.write("Last run 4 min ago")

        with r3c3.tile(
            "Form",
            caption=cap("Submit together"),
            icon=ico(":material/assignment:"),
            **common,
        ) as tile:
            kebab(tile, "w-form-menu")
            with st.form("w-form", border=False):
                st.text_input("Owner", key="w-form-owner")
                st.selectbox("Team", ["CS", "Sales", "RevOps"], key="w-form-team")
                st.form_submit_button("Create ticket", type="primary")

        r4c1, r4c2 = st.columns([2, 1])
        with r4c1.tile(
            "Data editor",
            caption=cap("Editable table inside a tile"),
            icon=ico(":material/table_edit:"),
            **common,
        ) as tile:
            kebab(tile, "w-editor-menu")
            st.data_editor(
                accounts.head(6),
                hide_index=True,
                height=240,
                disabled=["Account"],
                key="w-editor",
            )

        with r4c2.tile(
            "Disclosure",
            caption=cap("Expander and JSON"),
            icon=ico(":material/unfold_more:"),
            **common,
        ) as tile:
            kebab(tile, "w-disclose-menu")
            with st.expander("Query", expanded=True):
                st.code("select * from mrr_monthly", language="sql")
            st.json({"status": "live", "rows": 1284}, expanded=False)

elif example_page == "Advanced dashboard":
    st.subheader("Nimbus BI")
    st.caption("Certified KPIs, drill-down charts, and a top-accounts table.")
    f1, f2, f3 = st.columns(3)
    f1.pills(
        "Region",
        list(regions.index),
        selection_mode="multi",
        default=["North America", "Europe"],
        key="ex-dash-region",
    )
    f2.pills(
        "Plan",
        ["Starter", "Team", "Enterprise"],
        selection_mode="multi",
        default=["Team", "Enterprise"],
        key="ex-dash-plan",
    )
    f3.select_slider("Months", [3, 6, 12], value=12, key="ex-dash-months")

    kpis = st.columns(4)
    for col, (name, value, delta, series, kind) in zip(
        kpis,
        [
            ("ARR", "$4.2M", "+8%", mrr["Enterprise"], "area"),
            ("Net new MRR", "$186K", "+4%", mrr["Team"], "bar"),
            ("NRR", "112%", "+2pt", mrr_share["Enterprise"], "line"),
            ("Gross churn", "1.9%", "-0.3pt", mrr["Starter"], "bar"),
        ],
        strict=True,
    ):
        t = col.tile(
            name,
            icon=ico(":material/verified:"),
            help=tip("Certified metric, owned by RevOps."),
            **common,
        )
        live(t)
        t.metric(
            name,
            value,
            delta,
            chart_data=series,
            chart_type=kind,
            label_visibility="collapsed",
        )

    left, right = st.columns([3, 2])
    with left.tile(
        "MRR by plan",
        caption=cap("Monthly recurring revenue, stacked by plan"),
        icon=ico(":material/stacked_line_chart:"),
        **common,
    ) as tile:
        if show_actions:
            tile.actions.segmented_control(
                "View",
                ["$", "%"],
                default="$",
                key="ex-dash-mrr-view",
                label_visibility="collapsed",
            )
        kebab(tile, "ex-dash-mrr")
        live(tile)
        area_chart(mrr, height=280)

    with right.tile(
        "MRR bridge",
        caption=cap("How MRR moved over the last 12 months"),
        icon=ico(":material/account_tree:"),
        **common,
    ) as tile:
        kebab(tile, "ex-dash-bridge")
        live(tile)
        bridge = pd.Series(
            {"Start": 310, "New": 48, "Expansion": 62, "Churn": -28, "End": 392}
        )
        bar_chart(bridge, height=280)

    mix_col, table_col = st.columns([2, 3])
    with mix_col.tile(
        "Revenue by industry",
        caption=cap("Click a slice on the live app to filter accounts"),
        icon=ico(":material/pie_chart:"),
        **common,
    ) as tile:
        kebab(tile, "ex-dash-industry")
        industry = pd.Series(
            {"SaaS": 38, "Fintech": 22, "Healthcare": 18, "Retail": 14, "Other": 8}
        )
        bar_chart(industry, horizontal=True, height=260)

    with table_col.tile(
        "Top accounts",
        caption=cap("Largest customers by MRR"),
        icon=ico(":material/domain:"),
        **common,
    ) as tile:
        kebab(tile, "ex-dash-accounts")
        st.dataframe(accounts.head(8), hide_index=True, height=260)

elif example_page == "Apps that compute":
    st.subheader("Cairn Demand lab")
    st.caption("Move the levers, the forecast KPIs and charts update.")

    with st.tile(
        "Levers",
        caption=cap("Price, promo, marketing, and supply — no sidebar"),
        icon=ico(":material/tune:"),
        **common,
    ) as tile:
        kebab(tile, "ex-compute-levers")
        l1, l2, l3, l4, l5 = st.columns(5)
        product = l1.selectbox(
            "Product", ["Trail mix", "Bars", "Jerky"], key="ex-c-product"
        )
        price = l2.slider("Price vs plan", -10, 10, 0, format="%d%%", key="ex-c-price")
        promo = l3.slider("Promo", 0, 40, 15, format="%d%%", key="ex-c-promo")
        marketing = l4.slider("Marketing", 0.5, 2.0, 1.2, key="ex-c-mkt")
        supply = l5.slider("Supply", 70, 140, 110, format="%d%%", key="ex-c-supply")

    weeks = np.arange(26)
    lift = (
        (1 - 0.018 * price) * (1 + 0.012 * promo) * marketing * min(1.15, supply / 100)
    )
    units = np.clip(90 + weeks * 1.4 + rng.normal(0, 4, 26), 40, None) * lift
    revenue = units * (12 * (1 + price / 100) * (1 - promo / 200))
    profit = revenue - units * 4.8 - 18 * marketing
    stockout = np.clip((units / (supply / 100) - 140) / 80, 0, 1)
    fan = pd.DataFrame(
        {"P10": units * 0.82, "P50": units, "P90": units * 1.18},
        index=pd.date_range("2026-01-05", periods=26, freq="W"),
    )

    kpis = st.columns(4)
    for col, (name, value, delta, series, kind) in zip(
        kpis,
        [
            ("Units sold", f"{units.sum():,.0f}", "+6%", fan["P50"], "bar"),
            ("Revenue", f"${revenue.sum() / 1000:.1f}k", "+4%", fan["P50"], "area"),
            ("Profit", f"${profit.sum() / 1000:.1f}k", "+2%", fan["P50"], "area"),
            ("Stockout risk", f"{stockout.mean():.0%}", "+3pt", stockout, "bar"),
        ],
        strict=True,
    ):
        t = col.tile(name, icon=ico(":material/insights:"), **common)
        t.metric(
            name,
            value,
            delta,
            chart_data=series,
            chart_type=kind,
            label_visibility="collapsed",
        )

    left, right = st.columns([3, 2])
    with left.tile(
        "Weekly forecast",
        caption=cap(f"Median and ranges · {product}"),
        icon=ico(":material/show_chart:"),
        **common,
    ) as tile:
        if show_actions:
            tile.actions.segmented_control(
                "Measure",
                ["Units", "Revenue"],
                default="Units",
                key="ex-c-measure",
                label_visibility="collapsed",
            )
        kebab(tile, "ex-c-fan")
        area_chart(fan, height=320)

    with right.tile(
        "Forecast brief",
        caption=cap("Plain-language read of this scenario"),
        icon=ico(":material/notes:"),
        **common,
    ) as tile:
        kebab(tile, "ex-c-brief")
        st.markdown(
            f":material/insights: Profit is **{'up' if price >= 0 else 'down'}** vs. plan "
            f"with a **{promo}% promo** on {product}."
        )
        st.markdown(
            f":material/inventory_2: Supply at **{supply}%** leaves a "
            f"**{stockout.mean():.0%}** chance of selling out."
        )
        st.markdown(
            f":material/flag: **{min(96, 58 + promo + supply - 100):.0f}% chance** "
            "of hitting the revenue target."
        )
        st.markdown(
            ":material/lightbulb: Biggest upside: raise marketing before cutting price."
        )

    h1, h2 = st.columns(2)
    with h1.tile(
        "Season revenue outcomes",
        caption=cap("Share of simulated seasons vs. target"),
        icon=ico(":material/histogram:"),
        **common,
    ) as tile:
        kebab(tile, "ex-c-hist")
        draws = rng.normal(revenue.sum(), revenue.sum() * 0.12, 80)
        hist = pd.Series(draws).round(0).value_counts().sort_index()
        # Compact histogram via a line of binned counts.
        bins = pd.cut(draws, bins=8).value_counts().sort_index()
        bins.index = [f"{int(i.left / 1000)}k" for i in bins.index]
        bar_chart(bins, height=240)

    with h2.tile(
        "What moves profit",
        caption=cap("Each lever down vs. up"),
        icon=ico(":material/swap_horiz:"),
        **common,
    ) as tile:
        kebab(tile, "ex-c-tornado")
        tornado = pd.DataFrame(
            {"Down": [-18, -9, -22, -14], "Up": [12, 21, 16, 11]},
            index=["Price", "Promo", "Marketing", "Supply"],
        )
        bar_chart(tornado, horizontal=True, height=240)

elif example_page == "Workflow":
    st.subheader("Cairn Reorder desk")
    st.caption("Review queue: approve, adjust, or reject what the agent proposed.")

    q1, q2, q3, q4, q5 = st.columns(5)
    for col, (name, value, delta, icon) in zip(
        (q1, q2, q3, q4, q5),
        [
            ("Awaiting review", "18", "4 critical", ":material/inbox:"),
            ("Value awaiting", "$212k", "7 low risk", ":material/payments:"),
            ("Due today", "5", "cutoff 3:00 PM", ":material/schedule:"),
            ("Approved today", "$64k", "6 orders", ":material/local_shipping:"),
            ("Agent acceptance", "81%", "+4pt", ":material/smart_toy:"),
        ],
        strict=True,
    ):
        t = col.tile(name, icon=ico(icon), **common)
        t.metric(name, value, delta, label_visibility="collapsed")

    with st.tile(
        "Queue filters",
        icon=ico(":material/filter_list:"),
        **common,
    ) as tile:
        kebab(tile, "ex-wf-filters")
        f1, f2, f3 = st.columns([2, 3, 3])
        f1.segmented_control(
            "View",
            ["Awaiting review", "On hold", "Decided"],
            default="Awaiting review",
            key="ex-wf-view",
            label_visibility="collapsed",
        )
        f2.pills(
            "Category",
            ["Snacks", "Beverages", "Frozen", "Household"],
            selection_mode="multi",
            key="ex-wf-cat",
        )
        f3.text_input("Search", placeholder="SKU, supplier, or PO", key="ex-wf-search")

    queue = pd.DataFrame(
        {
            "Product": [
                "Trail mix 12oz",
                "Sparkling water 8pk",
                "Frozen berries",
                "Oat bars",
                "Almond butter",
                "Granola family",
            ],
            "DC": ["Austin", "Ohio", "Nevada", "Austin", "Ohio", "Nevada"],
            "Priority": ["Critical", "High", "High", "Medium", "Low", "Medium"],
            "Days left": [3, 5, 6, 9, 14, 8],
            "Agent qty": [420, 800, 260, 510, 140, 300],
            "Order qty": [420, 720, 260, 480, 140, 300],
            "Value": [18.4, 22.1, 9.6, 11.2, 6.1, 8.8],
            "Decision": [None, "Approve", None, None, "Hold", None],
            "Confidence": [91, 88, 64, 77, 82, 70],
        }
    )
    with st.tile(
        "Purchase orders",
        caption=cap("Edits stay as drafts until you submit"),
        icon=ico(":material/local_shipping:"),
        **common,
    ) as tile:
        kebab(tile, "ex-wf-table")
        live(tile)
        st.data_editor(
            queue,
            hide_index=True,
            height=300,
            disabled=[
                "Product",
                "DC",
                "Priority",
                "Days left",
                "Agent qty",
                "Value",
                "Confidence",
            ],
            column_config={
                "Value": st.column_config.NumberColumn("Value", format="$%.1fk"),
                "Decision": st.column_config.SelectboxColumn(
                    "Decision", options=["Approve", "Hold", "Reject"]
                ),
                "Confidence": st.column_config.ProgressColumn(
                    "Confidence", min_value=0, max_value=100, format="%d%%"
                ),
            },
            key="ex-wf-editor",
        )

    with st.tile(
        "Decision bar",
        caption=cap("Validate on submit"),
        icon=ico(":material/edit_note:"),
        **common,
    ) as tile:
        kebab(tile, "ex-wf-bar")
        b1, b2, b3, b4 = st.columns([3, 1, 1, 1])
        b1.markdown("**1 decision ready** · 1 to approve · $22.1k in orders")
        b2.button(
            "Review next",
            type="tertiary",
            icon=":material/play_arrow:",
            key="ex-wf-next",
        )
        b3.button(
            "Accept low-risk",
            type="tertiary",
            icon=":material/auto_awesome:",
            key="ex-wf-low",
        )
        b4.button(
            "Submit 1", type="primary", icon=":material/send:", key="ex-wf-submit"
        )

elif example_page == "Why tiles":
    st.subheader("What we are unlocking")
    st.markdown(
        """
- A **dashboard panel as a first-class layout**, not a homemade stack of
  heading + container + chart.
- A **consistent anatomy**: header (icon, title, caption, help, actions),
  body (any widgets, usually a chart or metric), footer (status like Live).
- **Actions that belong to the panel** — menus, toggles, and badges live on
  the tile instead of as extra widgets above or beside the chart.
- **Visual grouping that matches BI UIs**: outline, fill, divided header,
  accent bar, optional elevation.
- **Rows that line up**: tiles stretch to the row so four KPIs or a chart
  next to a table share a height.
"""
    )

    st.subheader("How this fills the gaps")
    st.markdown(
        """
- **Cards are homemade.** Today a panel is `st.container(border=True)` plus a
  subheader plus a chart. Every app invents that stack. A tile *is* that
  stack: `st.tile("ARR")` instead of assembling a card.
- **Titles don't belong to the chart.** `st.subheader` sits above the content
  and has no place for icon, help, or a menu. The tile header is the title
  *of the panel*, in the same chrome as the body.
- **Rows don't line up.** KPI and chart rows only look even if every sibling
  has the same parts, or you pass `height="stretch"` everywhere. Tiles
  stretch to the row by default.
- **Actions and status have nowhere to live.** Export, more-menu, “as of”,
  and Live get parked as extra widgets or in the sidebar. Chart toolbars
  also sit on the plot. Header is for panel actions; footer is for status
  (`tile.footer.badge("Live", …)`); chart toolbars hang on the tile edge.
- **Grouping is either too little or too much.** `border=True` is just a box.
  Fill, divider, accent, and elevation need CSS. `border`, `background`, and
  `variant` (`default` / `divided` / `accent`) give that surface language
  without custom CSS.
- **Filters get stuffed into the same box.** Because “card” is the only
  grouping tool, filters often look like another KPI. Tiles are for
  certified content (metric, chart, table). Filters stay outside as page
  chrome.
"""
    )
