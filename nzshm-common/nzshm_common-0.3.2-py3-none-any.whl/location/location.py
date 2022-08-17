# Omitting country for now, focus on NZ
# https://service.unece.org/trade/locode/nz.htm
LOCATIONS = [
    {"id": "AKL", "name": "Auckland", "latitude": -36.87, "longitude": 174.77},
    {"id": "BHE", "name": "Blenheim", "latitude": -41.51, "longitude": 173.95},
    {"id": "CHC", "name": "Christchurch", "latitude": -43.53, "longitude": 172.63},
    {"id": "DUD", "name": "Dunedin", "latitude": -45.87, "longitude": 170.5},
    {"id": "GIS", "name": "Gisborne", "latitude": -38.65, "longitude": 178.0},
    {"id": "GMN", "name": "Greymouth", "latitude": -42.45, "longitude": 171.21},
    {"id": "HAW", "name": "Hawera", "latitude": -39.59, "longitude": 174.28},
    {"id": "HLZ", "name": "Hamilton", "latitude": -37.78, "longitude": 175.28},
    {"id": "IVC", "name": "Invercargill", "latitude": -46.43, "longitude": 168.36},
    {"id": "KBZ", "name": "Kaikoura", "latitude": -42.4, "longitude": 173.68},
    {"id": "KKE", "name": "Kerikeri", "latitude": -35.22, "longitude": 173.97},
    {"id": "LVN", "name": "Levin", "latitude": -40.63, "longitude": 175.28},
    {"id": "MON", "name": "Mount Cook", "latitude": -43.73, "longitude": 170.1},
    {"id": "MRO", "name": "Masterton", "latitude": -40.96, "longitude": 175.66},
    {"id": "NPE", "name": "Napier", "latitude": -39.48, "longitude": 176.92},
    {"id": "NPL", "name": "New Plymouth", "latitude": -39.07, "longitude": 174.08},
    {"id": "NSN", "name": "Nelson", "latitude": -41.27, "longitude": 173.28},
    {"id": "PMR", "name": "Palmerston North", "latitude": -40.35, "longitude": 175.62},
    {"id": "TEU", "name": "Te Anau", "latitude": -45.41, "longitude": 167.72},
    {"id": "TIU", "name": "Timaru", "latitude": -44.4, "longitude": 171.26},
    {"id": "TKZ", "name": "Tokoroa", "latitude": -38.23, "longitude": 175.87},
    {"id": "TMZ", "name": "Thames", "latitude": -37.13, "longitude": 175.53},
    {"id": "TRG", "name": "Tauranga", "latitude": -37.69, "longitude": 176.17},
    {"id": "TUO", "name": "Taupo", "latitude": -38.68, "longitude": 176.08},
    {"id": "ROT", "name": "Rotorua", "latitude": -38.14, "longitude": 176.25},
    {"id": "WHK", "name": "Whakatane", "latitude": -37.98, "longitude": 177.0},
    {"id": "WHO", "name": "Franz Josef", "latitude": -43.35, "longitude": 170.17},
    {"id": "WLG", "name": "Wellington", "latitude": -41.3, "longitude": 174.78},
    {"id": "WSZ", "name": "Westport", "latitude": -41.75, "longitude": 171.58},
    {"id": "xx1", "name": "Whanganui", "latitude": -39.93, "longitude": 175.05},
    {"id": "xx2", "name": "Turangi", "latitude": -39.0, "longitude": 175.93},
    {"id": "xx3", "name": "Otira", "latitude": -42.78, "longitude": 171.54},
    {"id": "xx4", "name": "Haast", "latitude": -43.88, "longitude": 169.06},
    {"id": "xx5", "name": "Hanmer Springs", "latitude": -42.54, "longitude": 172.78},
    {"id": "ZQN", "name": "Queenstown", "latitude": -45.02, "longitude": 168.69},
]

LOCATIONS_BY_ID = {location["id"]: location for location in LOCATIONS}

LOCATION_LISTS = [
    {
        "id": "NZ",
        "name": "Default NZ locations",
        "locations": list(map(lambda loc: loc["id"], LOCATIONS)),
    },
    {
        "id": "NZ2",
        "name": "Main Cities NZ",
        "locations": ["WLG", "CHC", "DUD", "NPL", "AKL", "ROT", "HLZ"],
    },
]


def location_by_id(location_code):
    return LOCATIONS_BY_ID[location_code]


if __name__ == "__main__":
    """Print all locations."""
    print("custom_site_id,lon,lat")
    for loc in LOCATIONS:
        print(f"{loc['id']},{loc['longitude']},{loc['latitude']}")
