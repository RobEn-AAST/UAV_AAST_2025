import math
from typing import List, Tuple

# todo try to merge this with the utils/math

def haversine_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate the great-circle distance between two points on the Earth (Haversine formula).
    """
    lat1, lon1 = point1
    lat2, lon2 = point2
    R = 6371e3  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def compute_bearing(pointA: Tuple[float, float], pointB: Tuple[float, float]) -> float:
    """
    Compute the initial bearing from point A to point B in degrees.
    """
    latA, lonA = pointA
    latB, lonB = pointB
    phi1 = math.radians(latA)
    phi2 = math.radians(latB)
    delta_lambda = math.radians(lonB - lonA)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    theta = math.atan2(y, x)
    return math.degrees(theta) % 360.0

def cross_track_distance(pointA: Tuple[float, float], pointB: Tuple[float, float], pointP: Tuple[float, float]) -> float:
    """
    Calculate the cross-track distance from point P to the great circle path through points A and B.
    """
    R = 6371e3  # Earth radius in meters
    delta_AP = haversine_distance(pointA, pointP)
    bearing_AB = compute_bearing(pointA, pointB)
    bearing_AP = compute_bearing(pointA, pointP)
    delta_AP_rad = delta_AP / R
    theta_diff = math.radians(bearing_AP - bearing_AB)
    
    sin_xt = math.sin(delta_AP_rad) * math.sin(theta_diff)
    if sin_xt < -1:
        sin_xt = -1
    elif sin_xt > 1:
        sin_xt = 1
    xt_rad = math.asin(sin_xt)
    return abs(xt_rad * R)

def min_distance_to_segment(A: Tuple[float, float], B: Tuple[float, float], P: Tuple[float, float]) -> float:
    """
    Calculate the minimum distance from point P to the line segment AB.
    """
    AB_dist = haversine_distance(A, B)
    if AB_dist == 0:
        return haversine_distance(A, P)
    
    AP_dist = haversine_distance(A, P)
    BP_dist = haversine_distance(B, P)
    xt = cross_track_distance(A, B, P)
    
    R = 6371e3
    delta_AP_rad = AP_dist / R
    xt_rad = xt / R
    
    if xt_rad >= math.pi / 2:
        return min(AP_dist, BP_dist)
    
    try:
        ratio = math.cos(delta_AP_rad) / math.cos(xt_rad)
    except ZeroDivisionError:
        ratio = 1.0
    
    ratio = max(min(ratio, 1.0), -1.0)
    dat_rad = math.acos(ratio)
    dat = dat_rad * R
    
    if dat < 0 or dat > AB_dist:
        return min(AP_dist, BP_dist)
    else:
        return xt

def calc_path_cost(path: List[Tuple[float, float]], fence: List[list[float]], safety: int = 20) -> float:
    """
    Calculate the total cost of the UAV path, including penalties for proximity to the fence.
    """
    # todo what i there was no fence
    PENALTY_PER_VIOLATION = 2000  # Adjust penalty value as needed
    
    # Calculate total path distance
    total_distance = 0.0
    for i in range(len(path) - 1):
        total_distance += haversine_distance(path[i], path[i+1])
    
    # Prepare fence edges
    fence_edges = []
    for i in range(len(fence)):
        A = fence[i]
        B = fence[(i + 1) % len(fence)]
        fence_edges.append((A, B))
    
    # Check each point for proximity to the fence
    violation_count = 0
    for point in path:
        min_distances = []
        for A, B in fence_edges:
            dist = min_distance_to_segment(A, B, point)
            min_distances.append(dist)
        min_fence_dist = min(min_distances)
        if min_fence_dist < safety:
            violation_count += 1
            break # would i want to continue or no tho?
    
    total_cost = total_distance + violation_count * PENALTY_PER_VIOLATION
    return total_cost