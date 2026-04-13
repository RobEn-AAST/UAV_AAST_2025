import math
import numpy as np
from .geo_math import GeoCalculator  # UPDATE IMPORT

def is_obstacle_between(pointA, pointB, obstacle, radius):
    """Enhanced with geodesic precision"""
    return is_obstacle_between_geodesic(pointA, pointB, obstacle, radius)

def is_obstacle_between_geodesic(pointA, pointB, obstacle, radius):
    """Your existing geodesic implementation"""
    dist_A_obs = GeoCalculator.get_distance(pointA, obstacle)
    dist_B_obs = GeoCalculator.get_distance(pointB, obstacle)
    dist_A_B = GeoCalculator.get_distance(pointA, pointB)
    
    # Use triangle area formula to find perpendicular distance
    s = (dist_A_obs + dist_B_obs + dist_A_B) / 2
    if s * (s - dist_A_obs) * (s - dist_B_obs) * (s - dist_A_B) <= 0:
        return False
    
    area = math.sqrt(s * (s - dist_A_obs) * (s - dist_B_obs) * (s - dist_A_B))
    perpendicular_dist = (2 * area) / dist_A_B
    
    # Check if the closest point is within the segment
    bearing_A_B = GeoCalculator.get_bearing(pointA, pointB)
    bearing_A_obs = GeoCalculator.get_bearing(pointA, obstacle)
    
    # Projection parameter
    t = dist_A_obs * math.cos(math.radians(bearing_A_obs - bearing_A_B)) / dist_A_B
    
    return (0 <= t <= 1) and (perpendicular_dist <= radius)

def apply_obs_avoidance(wp_list: list[list[float]], obs_list: list[list[float]], safe_dist: float) -> list[list[float]]:
    """_summary_

    Args:
        wp_list (list[list[float]]): shape of [lat, long, alt]
        obs_list (list[list[float]]): shape of [lat, long, radius]

    Returns:
        list[list[float]]: shape of [lat, long, alt] after avoidance
    """
    newWaypoints = []

    def add_avoid_waypoint(
        latA,
        longA,
        altA,
        latB,
        longB,
        altB,
        obsLat,
        obsLong,
        obsRad,
        obsBearing,
        execludeObsI,
    ):
        dObs = obsRad + safe_dist

        latNew, longNew = GeoCalculator.new_waypoint(obsLat, obsLong, dObs, obsBearing)
        # check_obstacles(latA, longA, altA, latNew, longNew, altA, execludeObsI)
        newWaypoints.append([latNew, longNew, altA])
        # check_obstacles(latNew, longNew, altA, latB, longB, altB, execludeObsI)

    def check_obstacles(latA, longA, altA, latB, longB, altB, execludeObsI):
        for i, obs in enumerate(obs_list):
            if execludeObsI is not None and i == execludeObsI:
                continue

            ObsLat, ObsLong, ObsRad = obs

            is_obstacle_between(
                [latA, longA], [latB, longB], [ObsLat, ObsLong], ObsRad + safe_dist
            )
            distance_a_b = GeoCalculator.get_distance([latA, longA], [latB, longB])
            distance_a_obs = GeoCalculator.get_distance([latA, longA], [ObsLat, ObsLong])
            bearing_a_obs = GeoCalculator.get_bearing([latA, longA], [ObsLat, ObsLong])
            bearing_a_b = GeoCalculator.get_bearing([latA, longA], [latB, longB])
            bearingObs = bearing_a_b - 90

            if bearing_a_b > bearing_a_obs:
                brng = bearing_a_b - bearing_a_obs
            else:
                brng = bearing_a_obs - bearing_a_b

            obsAffects = is_obstacle_between(
                [latA, longA], [latB, longB], [ObsLat, ObsLong], ObsRad + safe_dist
            )
            if obsAffects:
                add_avoid_waypoint(
                    latA,
                    longA,
                    altA,
                    latB,
                    longB,
                    altB,
                    ObsLat,
                    ObsLong,
                    ObsRad,
                    bearingObs,
                    i,
                )

    if len(obs_list) == 0:
        for i, wp in enumerate(wp_list):
            newWaypoints.append([wp[0], wp[1], wp[2]])

    else:
        # combine close obstacles
        i = 0
        while i < len(obs_list) - 1:
            obs = obs_list[i]
            nextObs = obs_list[i + 1]
            distance = GeoCalculator.get_distance([obs[0], obs[1]], [nextObs[0], nextObs[1]])
            bearing = GeoCalculator.get_bearing([obs[0], obs[1]], [nextObs[0], nextObs[1]])
            if abs(distance) <= 30:
                ObsLat_new, ObsLong_new = GeoCalculator.new_waypoint(
                    obs[0], obs[1], distance / 2, bearing
                )
                # ! TEST THE NEW RADIUS IMPLEMENTATION INSTEAD OF JUST ADDING
                obsRadius = obs[2] + nextObs[2]  # math.sqrt(obs[2]**2 + nextObs[2]**2)
                obs_list[i] = [ObsLat_new, ObsLong_new, obsRadius]
                del obs_list[i + 1]
            else:
                i += 1

        firstWp = wp_list[0]
        newWaypoints.append([firstWp[0], firstWp[1], firstWp[2]])
        for i, wp in enumerate(wp_list[:-1]):
            nextWp = wp_list[i + 1]
            latA, longA, altA = wp[0], wp[1], wp[2]
            latB, longB, altB = nextWp[0], nextWp[1], nextWp[2]

            check_obstacles(latA, longA, altA, latB, longB, altB, None)

            newWaypoints.append([latB, longB, altB])

    return newWaypoints