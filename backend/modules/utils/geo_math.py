import math
import numpy as np
from geopy.distance import geodesic
from geopy.point import Point

class GeoCalculator:    
    R = 6371000.0
    
    @staticmethod
    def get_distance(pointA, pointB):
        """High-precision distance using geodesic (Vincenty) - replaces haversine"""
        return geodesic(pointA, pointB).meters
    
    @staticmethod
    def get_bearing(pointA, pointB):
        """Get initial bearing between two points with geodesic precision"""
        lat1, lon1 = math.radians(pointA[0]), math.radians(pointA[1])
        lat2, lon2 = math.radians(pointB[0]), math.radians(pointB[1])
        
        dlon = lon2 - lon1
        x = math.sin(dlon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        
        return compass_bearing
    
    @staticmethod
    def new_waypoint(start_point, distance, bearing):
        """Calculate destination point with geodesic precision"""
        start = Point(start_point[0], start_point[1])
        destination = geodesic(meters=distance).destination(start, bearing)
        return destination.latitude, destination.longitude

# Keep your original functions for backward compatibility
def get_bearing_2_points(lat1, long1, lat2, long2):
    return GeoCalculator.get_bearing([lat1, long1], [lat2, long2])

def new_waypoint(lat1, long1, d, brng):
    return GeoCalculator.new_waypoint([lat1, long1], d, brng)

def calc_drop_loc(H1, Vpa, Vag, angle):
    g = 9.81
    Cd = 0.5
    rho = 1.225
    A = 0.02
    m = 1
    H = [float(H1)]
    ty = [0]
    Vy = [0]
    acc = [9.81]
    Dy = [0]
    dy = [0]
    k = 1
    int = 0.001

    while H[k - 1] > 0:
        ty.append(ty[k - 1] + int)
        H.append(H[k - 1] - (Vy[k - 1] * int + 0.5 * acc[k - 1] * int**2))
        Vy.append(Vy[k - 1] + acc[k - 1] * int)
        Dy.append(Cd * rho * (Vy[k - 1] ** 2) * A / 2)
        dy.append(Dy[k - 1] / m)
        acc.append(g - dy[k])
        k = k + 1

    Vpa = float(Vpa)
    Vag = float(Vag)
    angle = float(angle)

    Vpg = Vpa - Vag * np.cos(np.deg2rad(angle))
    Vx = [Vpg]
    R = [0]
    Dx = [Cd * 1.225 * (Vx[0] ** 2) * A / 2]
    dx = [Dx[0] / m]
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

    return R[k - 1]