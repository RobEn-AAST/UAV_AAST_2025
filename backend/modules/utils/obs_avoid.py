# TODO TEST
from .math import get_dist_2_points, get_bearing_2_points, new_waypoint, haversine
import numpy as np


def is_obstacle_between(pointA, pointB, obstacle, radius):
    # Extract coordinates
    pointA_lat, pointA_long = pointA
    pointB_lat, pointB_long = pointB
    obstacle_lat, obstacle_long = obstacle

    # Convert coordinates to Cartesian (X, Y) for easier calculations
    def latlon_to_xy(lat, lon):
        return (lat, lon)

    Ax, Ay = latlon_to_xy(pointA_lat, pointA_long)
    Bx, By = latlon_to_xy(pointB_lat, pointB_long)
    Ox, Oy = latlon_to_xy(obstacle_lat, obstacle_long)

    # Vector AB and AO
    AB = np.array([Bx - Ax, By - Ay])
    AO = np.array([Ox - Ax, Oy - Ay])

    # Project AO onto AB to find the closest point on the line segment
    AB_squared = np.dot(AB, AB)
    if AB_squared == 0:
        return False  # A and B are the same point

    AO_dot_AB = np.dot(AO, AB)
    t = AO_dot_AB / AB_squared
    t = max(0, min(1, t))  # Clamp t to the range [0, 1]

    # Find the projection point
    projection = np.array([Ax, Ay]) + t * AB

    # Distance from the obstacle to the projection point
    distance_to_obstacle = haversine(
        projection[0], projection[1], obstacle_lat, obstacle_long
    )

    return distance_to_obstacle <= radius


safetyMargin = 0
pointsAroundObs = 1


def apply_obs_avoidance(
    wp_list: list[list[float]], obs_list: list[list[float]], safe_dist: float
) -> list[list[float]]:
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

        latNew, longNew = new_waypoint(obsLat, obsLong, dObs, obsBearing)
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
            distance_a_b = get_dist_2_points(latA, longA, latB, longB)
            distance_a_obs = get_dist_2_points(latA, longA, ObsLat, ObsLong)
            bearing_a_obs = get_bearing_2_points(latA, longA, ObsLat, ObsLong)
            bearing_a_b = get_bearing_2_points(latA, longA, latB, longB)
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
            distance = get_dist_2_points(obs[0], obs[1], nextObs[0], nextObs[1])
            bearing = get_bearing_2_points(obs[0], obs[1], nextObs[0], nextObs[1])
            if abs(distance) <= 30:
                ObsLat_new, ObsLong_new = new_waypoint(
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
