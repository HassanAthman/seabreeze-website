"""Where Seabreeze agents work: counties covered, their page slugs, and map pins.

Used by tools/art.py (maps), tools/pages.py (area pages) and tools/cards.py
(share images). Add a county here, then run the three tools.
"""

# Area pages. slug -> details. kind "county" covers the whole county;
# kind "town" is a single town page inside a county that has its own page.
# region decides which close-up map the page shows.
AREAS = {
    # Coast
    "malindi": dict(kind="town", name="Malindi", county="Kilifi", region="coast", keep=True),
    "kilifi": dict(kind="county", name="Kilifi", region="coast",
                   towns=["Kilifi town", "Mtwapa", "Watamu", "Gede", "Mariakani", "Kaloleni", "Mazeras", "Rabai", "Ganze"],
                   note="Malindi, our head office town, has its own page."),
    "mombasa": dict(kind="county", name="Mombasa", region="coast",
                    towns=["Mombasa Island", "Nyali", "Bamburi", "Shanzu", "Kisauni", "Likoni", "Changamwe", "Port Reitz", "Jomvu", "Tudor"]),
    "kwale": dict(kind="county", name="Kwale", region="coast",
                  towns=["Ukunda", "Diani", "Tiwi", "Kwale town", "Matuga", "Kinango", "Msambweni", "Shimoni", "Lunga Lunga"]),
    "lamu": dict(kind="county", name="Lamu", region="coast",
                 towns=["Lamu town", "Shela", "Mokowe", "Hindi", "Witu", "Faza", "Kiunga"],
                 note="Mpeketoni has its own page."),
    "mpeketoni": dict(kind="town", name="Mpeketoni", county="Lamu", region="coast", keep=True),
    "tana-river": dict(kind="county", name="Tana River", region="coast",
                       towns=["Hola", "Garsen", "Bura", "Madogo", "Tarasaa", "Kipini", "Minjila"]),
    "voi": dict(kind="town", name="Voi", county="Taita Taveta", region="coast", keep=True),
    # Nairobi
    "nairobi": dict(kind="county", name="Nairobi", region="rift",
                    towns=["Nairobi CBD", "Westlands", "Kilimani", "Kileleshwa", "Lavington", "Karen", "Lang'ata", "South B",
                           "South C", "Embakasi", "Donholm", "Kayole", "Ruai", "Kasarani", "Roysambu", "Ruaraka", "Dagoretti", "Kibra"]),
    # Western and Nyanza
    "kisumu": dict(kind="county", name="Kisumu", region="rift",
                   towns=["Kisumu city", "Milimani", "Nyalenda", "Kondele", "Mamboleo", "Maseno", "Kombewa", "Ahero", "Muhoroni"]),
    "kakamega": dict(kind="county", name="Kakamega", region="rift",
                     towns=["Kakamega town", "Khayega", "Mumias", "Butere", "Malava", "Lugari", "Shinyalu"]),
    "bungoma": dict(kind="county", name="Bungoma", region="rift",
                    towns=["Bungoma town", "Webuye", "Kimilili", "Chwele", "Sirisia", "Malakisi", "Tongaren"]),
    # Former Rift Valley Province
    "turkana": dict(kind="county", name="Turkana", region="rift",
                    towns=["Lodwar", "Kakuma", "Lokichogio", "Lokichar", "Kalokol", "Lokori"]),
    "kapenguria": dict(kind="county", name="West Pokot", region="rift", title_place="Kapenguria and West Pokot",
                       towns=["Kapenguria", "Makutano", "Chepareria", "Ortum", "Sigor", "Kacheliba"]),
    "samburu": dict(kind="county", name="Samburu", region="rift",
                    towns=["Maralal", "Kisima", "Baragoi", "Wamba", "Archers Post"]),
    "trans-nzoia": dict(kind="county", name="Trans Nzoia", region="rift",
                        towns=["Kitale", "Kiminini", "Endebess", "Saboti", "Moi's Bridge", "Kachibora"]),
    "uasin-gishu": dict(kind="county", name="Uasin Gishu", region="rift",
                        towns=["Eldoret", "Kapseret", "Kesses", "Burnt Forest", "Turbo", "Moiben", "Ziwa"]),
    "elgeyo-marakwet": dict(kind="county", name="Elgeyo-Marakwet", region="rift",
                            towns=["Iten", "Tambach", "Chepkorio", "Kapsowar", "Chesoi", "Kamwosor"]),
    "kapsabet": dict(kind="county", name="Nandi", region="rift", title_place="Kapsabet and Nandi",
                     towns=["Kapsabet", "Nandi Hills", "Mosoriot", "Kobujoi", "Lessos", "Kaiboi"]),
    "baringo": dict(kind="county", name="Baringo", region="rift",
                    towns=["Kabarnet", "Eldama Ravine", "Marigat", "Mogotio", "Kabartonjo", "Chemolingot"]),
    "laikipia": dict(kind="county", name="Laikipia", region="rift",
                     towns=["Nanyuki", "Nyahururu", "Rumuruti", "Doldol", "Kinamba"]),
    "nakuru": dict(kind="county", name="Nakuru", region="rift",
                   towns=["Nakuru city", "Naivasha", "Gilgil", "Njoro", "Molo", "Rongai", "Subukia", "Mai Mahiu", "Salgaa"]),
    "narok": dict(kind="county", name="Narok", region="rift",
                  towns=["Narok town", "Kilgoris", "Ololulunga", "Nairegie Enkare", "Suswa", "Talek"]),
    "kajiado": dict(kind="county", name="Kajiado", region="rift",
                    towns=["Kitengela", "Ongata Rongai", "Ngong", "Kiserian", "Isinya", "Kajiado town", "Namanga", "Loitokitok"]),
    "kericho": dict(kind="county", name="Kericho", region="rift",
                    towns=["Kericho town", "Litein", "Londiani", "Kipkelion", "Sosiot", "Fort Ternan"]),
    "bomet": dict(kind="county", name="Bomet", region="rift",
                  towns=["Bomet town", "Sotik", "Longisa", "Mulot", "Silibwet"]),
}

GROUPS = [
    ("Coast", ["malindi", "kilifi", "mombasa", "kwale", "lamu", "mpeketoni", "tana-river", "voi"]),
    ("Nairobi", ["nairobi"]),
    ("Rift Valley", ["turkana", "kapenguria", "samburu", "trans-nzoia", "uasin-gishu", "elgeyo-marakwet", "kapsabet",
                     "baringo", "laikipia", "nakuru", "narok", "kajiado", "kericho", "bomet"]),
    ("Western and Nyanza", ["kisumu", "kakamega", "bungoma"]),
]

def chip_label(slug):
    a = AREAS[slug]
    if slug == "malindi":
        return "Malindi (head office)"
    return a["name"] + (" County" if a["kind"] == "county" else "")

# Map pins: (label, lon, lat, page slug, {view: (side, dy)}). A view missing
# from the dict means the pin has no label there (it still shows, with a tooltip),
# except on close-up maps, where a pin outside the view is skipped.
# sides: r right, l left, a above, b below
PINS = [
    ("Malindi", 40.12, -3.22, "malindi", {"kenya": ("r", 0), "coast": ("r", 0)}),
    ("Kilifi", 39.85, -3.63, "kilifi", {"coast": ("r", 0)}),
    ("Mombasa", 39.67, -4.05, "mombasa", {"kenya": ("r", 2), "coast": ("r", 0)}),
    ("Kwale", 39.45, -4.17, "kwale", {"coast": ("l", 0)}),
    ("Diani", 39.57, -4.29, "kwale", {"coast": ("r", 2)}),
    ("Msambweni", 39.48, -4.47, "kwale", {"coast": ("r", 4)}),
    ("Lunga Lunga", 39.12, -4.55, "kwale", {"coast": ("l", 0)}),
    ("Lamu", 40.90, -2.27, "lamu", {"kenya": ("r", 0), "coast": ("r", 0)}),
    ("Mpeketoni", 40.69, -2.39, "mpeketoni", {"coast": ("b", 0)}),
    ("Witu", 40.44, -2.39, "lamu", {"coast": ("l", 0)}),
    ("Garsen", 40.12, -2.27, "tana-river", {"coast": ("l", 0)}),
    ("Hola", 40.03, -1.50, "tana-river", {"kenya": ("r", 0), "coast": ("r", 0)}),
    ("Bura", 39.95, -1.10, "tana-river", {"coast": ("r", 0)}),
    ("Voi", 38.56, -3.40, "voi", {"kenya": ("l", 0), "coast": ("l", 0)}),
    ("Nairobi", 36.82, -1.29, "nairobi", {"kenya": ("r", 0), "rift": ("r", 0)}),
    ("Kitengela", 36.96, -1.47, "kajiado", {"rift": ("r", 4)}),
    ("Kajiado", 36.79, -1.85, "kajiado", {"rift": ("r", 0)}),
    ("Kisumu", 34.76, -0.09, "kisumu", {"kenya": ("l", 0), "rift": ("l", 0)}),
    ("Kakamega", 34.75, 0.28, "kakamega", {"rift": ("l", 4)}),
    ("Bungoma", 34.56, 0.56, "bungoma", {"rift": ("l", -2)}),
    ("Lodwar", 35.60, 3.12, "turkana", {"kenya": ("r", 0), "rift": ("r", 0)}),
    ("Kakuma", 34.86, 3.72, "turkana", {"rift": ("r", 0)}),
    ("Kapenguria", 35.12, 1.24, "kapenguria", {"rift": ("r", 0)}),
    ("Maralal", 36.70, 1.10, "samburu", {"kenya": ("r", 0), "rift": ("r", 0)}),
    ("Kitale", 35.00, 1.02, "trans-nzoia", {"rift": ("l", 0)}),
    ("Eldoret", 35.27, 0.52, "uasin-gishu", {"kenya": ("l", 0), "rift": ("b", 0)}),
    ("Iten", 35.51, 0.67, "elgeyo-marakwet", {"rift": ("r", -2)}),
    ("Kapsabet", 35.10, 0.20, "kapsabet", {"rift": ("r", 2)}),
    ("Kabarnet", 35.74, 0.49, "baringo", {"rift": ("r", 4)}),
    ("Nanyuki", 37.07, 0.02, "laikipia", {"kenya": ("r", 0), "rift": ("r", 0)}),
    ("Nyahururu", 36.36, 0.04, "laikipia", {"rift": ("b", 0)}),
    ("Nakuru", 36.07, -0.30, "nakuru", {"kenya": ("r", 2), "rift": ("r", 2)}),
    ("Naivasha", 36.43, -0.72, "nakuru", {"rift": ("r", 0)}),
    ("Narok", 35.87, -1.08, "narok", {"rift": ("l", 0)}),
    ("Kericho", 35.29, -0.37, "kericho", {"rift": ("l", 0)}),
    ("Bomet", 35.34, -0.78, "bomet", {"rift": ("l", 0)}),
]

def pins_for(slug):
    return {p[0] for p in PINS if p[3] == slug}
