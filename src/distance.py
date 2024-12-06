from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000.0

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

# lat1, lon1 = 54.725223, 55.940823  # Точка перекрекстка
# lat2, lon2 = 54.725282, 55.940433  # Точка перекрекстка
# print(f"Расстояние: {haversine_distance(lat1, lon1, lat2, lon2):.2f} м")