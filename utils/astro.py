import swisseph as swe
from datetime import datetime
import math
import sys

AYANAMSAS = {
    "lahiri": swe.SIDM_LAHIRI,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "bvraman": swe.SIDM_RAMAN,
}


def normalize360(x):
    a = math.fmod(x, 360.0)
    return (a + 360.0) if a < 0 else a


class Astro:
    def __init__(self, ayanamsa: str = "lahiri"):
        # sepl_18.se1 & semo_18.se1 files are expected here
        swe.set_ephe_path("data")
        swe.set_sid_mode(AYANAMSAS[ayanamsa])

    def get_sky_details(self, dt_utc: datetime):
        out = {}
        planets = {
            "sun": swe.SUN,
            "moon": swe.MOON,
            "mars": swe.MARS,
            "mercury": swe.MERCURY,
            "jupiter": swe.JUPITER,
            "venus": swe.VENUS,
            "saturn": swe.SATURN,
            "rahu": swe.MEAN_NODE,
            "ketu": None,
        }

        # FIXME debug
        print(f"astro: {dt_utc}")
        sys.stdout.flush()

        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + (dt_utc.minute / 60),
            swe.GREG_CAL,
        )
        print(f"jd: {jd}")
        sys.stdout.flush()

        for planet, pcode in planets.items():
            out[planet] = {}
            if pcode is None:
                continue

            try:
                coords, _ = swe.calc_ut(
                    jd, pcode, flags=swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
                )
                lon, lat, dist, dlon, dlat, dr = coords
                out[planet]["lon"] = lon
                out[planet]["dlon"] = dlon
                print(f"{planet}: {lon}")
                sys.stdout.flush()
            except Exception as e:
                print(f"exception {planet}: {e}")

        # calculate ketu
        out["ketu"]["lon"] = normalize360(out["rahu"]["lon"] + 180)
        out["ketu"]["dlon"] = out["rahu"]["dlon"]

        return out
