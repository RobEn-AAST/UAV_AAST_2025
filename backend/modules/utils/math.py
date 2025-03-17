import math
import numpy as np

R = 6371000.0  # Earth radius in meters


def get_dist_2_points(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    km = 6371 * c
    return km * 1000


def haversine(lat1, lon1, lat2, lon2):
    # Calculate the great-circle distance between two points on the Earth's surface.
    R = 6371000  # Earth radius in meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = (
        np.sin(delta_phi / 2.0) ** 2
        + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def deg_to_rad(lat, lon):  # Convert LAT & LONG from degree to radian
    lat = float(lat) * math.pi / 180
    lon = float(lon) * math.pi / 180
    return lat, lon


def rad_to_deg(lat, lon):  # Convert LAT & LONG from radian to degree
    lat = float(lat) * 180 / math.pi
    lon = float(lon) * 180 / math.pi
    return lat, lon


def distance(LatA, LongA, LatB, LongB):  # Get distance between 2 points
    LatA_r, LongA_r = deg_to_rad(LatA, LongA)
    LatB_r, LongB_r = deg_to_rad(LatB, LongB)
    LatAB_r = LatB_r - LatA_r
    LongAB_r = LongB_r - LongA_r
    a = ((math.sin(LatAB_r / 2)) * (math.sin(LatAB_r / 2))) + math.cos(
        LatA_r
    ) * math.cos(LatB_r) * ((math.sin(LongAB_r / 2)) * (math.sin(LongAB_r / 2)))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def get_bearing_2_points(lat1, long1, lat2, long2):  # get bearing between 2 points
    lat1_r, long1_r = deg_to_rad(lat1, long1)
    lat2_r, long2_r = deg_to_rad(lat2, long2)
    y = math.sin(long2_r - long1_r) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(
        lat2_r
    ) * math.cos(long2_r - long1_r)
    i = math.atan2(y, x)
    bearing = (i * 180 / math.pi + 360) % 360
    return bearing


def new_waypoint(lat1, long1, d, brng):
    brng *= math.pi / 180
    lat1, long1 = math.radians(lat1), math.radians(long1)
    lat2_r = math.asin(
        math.sin(lat1) * math.cos(d / R)
        + math.cos(lat1) * math.sin(d / R) * math.cos(brng)
    )
    long2_r = long1 + math.atan2(
        (math.sin(brng) * math.sin(d / R) * math.cos(lat1)),
        (math.cos(d / R) - math.sin(lat1) * math.sin(lat2_r)),
    )
    return math.degrees(lat2_r), math.degrees(long2_r)


def calc_drop_loc(H1, Vpa, Vag, angle):
    g = 9.81  # acceleration due to gravity
    Cd = 0.5  # drag coefficient of payloads
    rho = 1.225  # density of air
    A = 0.02  # average cross section of the payload
    m = 1  # mass of the payload
    H = [float(H1)]  # height of the plane in meters
    ty = [0]  # duration of fall
    Vy = [0]  # velocity in downward direction
    acc = [9.81]  # acceleration in downward direction
    Dy = [0]  # upward drag force
    dy = [0]  # deceleration due to drag force
    k = 1
    int = 0.001  # time intervals for calculation in the loops

    while H[k - 1] > 0:
        ty.append(ty[k - 1] + int)
        H.append(H[k - 1] - (Vy[k - 1] * int + 0.5 * acc[k - 1] * int**2))
        Vy.append(Vy[k - 1] + acc[k - 1] * int)
        Dy.append(Cd * rho * (Vy[k - 1] ** 2) * A / 2)
        dy.append(Dy[k - 1] / m)
        acc.append(g - dy[k])
        k = k + 1

    print("££££££££££££££££££££££££££££££")
    print("Duration of free-fall:", ty[k - 1], "sec")
    print("££££££££££££££££££££££££££££££")

    Vpa = float(Vpa)  # cruising velocity in m/s
    Vag = float(Vag)  # velocity of wind wrt to ground in m/s
    angle = float(angle)  # angle of Vag in degrees

    Vpg = Vpa - Vag * np.cos(np.deg2rad(angle))  # velocity of plane wrt ground
    Vx = [Vpg]  # velocity of payload in horizontal direction
    R = [0]  # distance covered by payload in horizontal direction
    Dx = [Cd * 1.225 * (Vx[0] ** 2) * A / 2]  # horizontal drag on the payload
    dx = [Dx[0] / m]  # horizontal deceleration on the payload
    k = 1

    Vx = np.append(Vx, np.zeros(len(ty) - 1))
    R = np.append(R, np.zeros(len(ty) - 1))
    Dx = np.append(Dx, np.zeros(len(ty) - 1))
    dx = np.append(dx, np.zeros(len(ty) - 1))

    for tx in range(len(ty) - 1):
        R[k] = R[k - 1] + (Vx[k - 1] * int - 0.5 * dx[k - 1] * int**2)
        Vx[k] = Vx[k - 1] - dx[k - 1] * int
        Dx[k] = (Cd * 1.225 * 0.5 * A) * (Vx[k] ** 2)
        dx[k] = Dx[k] / m
        k = k + 1

    print("££££££££££££££££££££££££££££££")
    print("Range of payload", (R[k - 1]), "meter")
    print("££££££££££££££££££££££££££££££")
    x = R[k - 1]
    y = H1
    return x


if __name__ == '__main__':
    p1 = [-35.3631385,	149.1607118]
    p2 = [-35.3594462, 149.1606045]
    print(get_bearing_2_points(*p1, *p2))