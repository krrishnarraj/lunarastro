import numpy as np
import plotly.graph_objects as go
from streamlit import cache_data


# ------------------------------------------------------------------ #
# static (cached) dictionaries
# ------------------------------------------------------------------ #
@cache_data
def static_data():
    houses = [
        "Mesha",
        "Vrishabha",
        "Mithuna",
        "Karka",
        "Simha",
        "Kanya",
        "Tula",
        "Vrishchika",
        "Dhanu",
        "Makara",
        "Kumbha",
        "Meena",
    ]

    element_colour = {  # fire / earth / air / water
        0: "rgba(255,182,193,0.30)",
        1: "rgba(144,238,144,0.30)",
        2: "rgba(255,255,180,0.30)",
        3: "rgba(173,216,230,0.30)",
        4: "rgba(255,182,193,0.30)",
        5: "rgba(144,238,144,0.30)",
        6: "rgba(255,255,180,0.30)",
        7: "rgba(173,216,230,0.30)",
        8: "rgba(255,182,193,0.30)",
        9: "rgba(144,238,144,0.30)",
        10: "rgba(255,255,180,0.30)",
        11: "rgba(173,216,230,0.30)",
    }

    planet_sym = dict(
        sun="☉",
        moon="☽",
        mars="♂",
        mercury="☿",
        jupiter="♃",
        venus="♀",
        saturn="♄",
        rahu="☊",
        ketu="☋",
    )
    planet_name = {p: p.title() for p in planet_sym}
    planet_col = dict(
        sun="#CC4400",
        moon="#666666",
        mars="#990000",
        mercury="#006600",
        jupiter="#CC9900",
        venus="#CC0066",
        saturn="#000099",
        rahu="#4D2D00",
        ketu="#4D2D00",
    )
    return houses, element_colour, planet_sym, planet_name, planet_col


@cache_data
def degree_marks():
    marks = []
    for deg in range(0, 360, 5):
        ih = deg % 30
        major = ih % 10 == 0
        marks.append(
            dict(
                deg=deg,
                r0=1.00,
                r1=1.06 if major else 1.03,
                width=2 if major else 1,
                label=f"{ih}°" if major else None,
            )
        )
    return marks


# ------------------------------------------------------------------ #
# small helpers
# ------------------------------------------------------------------ #
def astro_house(lon):  # 0-11
    return int(lon // 30)


def deg_in_house(lon):
    return lon % 30


def deg_min(x):
    d = int(x)
    m = int(round((x - d) * 60))
    return d, m


# ------------------------------------------------------------------ #
# figure creation
# ------------------------------------------------------------------ #
def build_chart(planets):
    houses, colours, psym, pname, pcol = static_data()
    fig = go.Figure()

    # coloured sectors
    for i in range(12):
        t0, t1 = i * 30, (i + 1) * 30
        theta = np.linspace(np.radians(t0), np.radians(t1), 16)
        fig.add_trace(
            go.Scatterpolar(
                r=np.append(np.ones_like(theta) * 1.00, np.ones_like(theta) * 0.80),
                theta=np.append(np.degrees(theta), np.degrees(theta)[::-1]),
                fill="toself",
                fillcolor=colours[i],
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
            )
        )

    # borders
    circle_t = np.linspace(0, 360, 145)
    for r in (1.00, 0.80):
        fig.add_trace(
            go.Scatterpolar(
                r=[r] * len(circle_t),
                theta=circle_t,
                mode="lines",
                line=dict(color="gray", width=2),
                hoverinfo="skip",
            )
        )

    # spokes & labels
    for i in range(12):
        ang = i * 30
        fig.add_trace(
            go.Scatterpolar(
                r=[0.80, 1.00],
                theta=[ang, ang],
                mode="lines",
                line=dict(color="gray", width=2),
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatterpolar(
                r=[0.90],
                theta=[ang + 15],
                mode="text",
                text=[houses[i]],
                textfont=dict(size=14),
                hoverinfo="skip",
            )
        )

    # degree ticks
    for mk in degree_marks():
        fig.add_trace(
            go.Scatterpolar(
                r=[mk["r0"], mk["r1"]],
                theta=[mk["deg"], mk["deg"]],
                mode="lines",
                line=dict(color="gray", width=mk["width"]),
                hoverinfo="skip",
            )
        )
        if mk["label"]:
            fig.add_trace(
                go.Scatterpolar(
                    r=[1.11],
                    theta=[mk["deg"]],
                    mode="text",
                    text=[mk["label"]],
                    textfont=dict(size=10),
                    hoverinfo="skip",
                )
            )

    # planets grouped by house
    buckets = {}
    for pl, data in planets.items():
        buckets.setdefault(astro_house(data["lon"]), []).append((pl, data))

    for h, plist in buckets.items():
        for idx, (pl, data) in enumerate(plist):
            ang = data["lon"]
            r = 0.65 - idx * 0.08
            d, m = deg_min(deg_in_house(data["lon"]))
            retro = data["dlon"] < 0
            fig.add_trace(
                go.Scatterpolar(
                    r=[r],
                    theta=[ang],
                    mode="markers+text",
                    marker=dict(
                        size=24,
                        color=pcol[pl],
                        line=dict(
                            color="#8B0000" if retro else "gray",
                            width=3 if retro else 1,
                        ),
                    ),
                    text=[psym[pl]],
                    textposition="middle center",
                    textfont=dict(size=16, color="white", family="Arial Black"),
                    hovertemplate=(
                        f"<b>{pname[pl]}</b><br>"
                        f"{d}° {m:02d}'<br>"
                        f"Speed : {data['dlon']:.4f}°/d"
                        f"{' (℞)' if retro else ''}<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=False, range=[0, 1.2]),
            angularaxis=dict(
                tickmode="linear",
                tick0=0,
                dtick=30,
                direction="clockwise",
                rotation=90,
                showticklabels=False,
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=800,
    )
    return fig
