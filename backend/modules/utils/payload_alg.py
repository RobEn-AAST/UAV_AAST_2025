from .geo_math import new_waypoint
def get_payload_approach_bearing(fence_list, payload_pos, shrink_ratio=0.95):
    if not fence_list:
        raise ValueError("Fence list cannot be empty")

    # Bounding rectangle of original fence
    lats = [pt[0] for pt in fence_list]
    lons = [pt[1] for pt in fence_list]

    top, bottom = max(lats), min(lats)
    left, right = min(lons), max(lons)

    # Shrink rectangle to stay inside fence
    lat_center = (top + bottom) / 2
    lon_center = (left + right) / 2

    half_height = (top - bottom) / 2 * shrink_ratio
    half_width  = (right - left) / 2 * shrink_ratio

    temp_top = lat_center + half_height
    temp_bottom = lat_center - half_height
    temp_left = lon_center - half_width
    temp_right = lon_center + half_width

    # Decide split direction
    width = temp_right - temp_left
    height = temp_top - temp_bottom

    payload_lat, payload_lon = payload_pos[0], payload_pos[1]

    if height >= width:
        # Split horizontally
        mid_lat = (temp_top + temp_bottom) / 2
        if payload_lat > mid_lat:
            return 0    
        else:
            return 180  
    '''else:
        # Split vertically: left vs right
        mid_lon = (temp_left + temp_right) / 2
        if payload_lon > mid_lon:
            return 90   # left → right
        else:
            return 270  # right → left'''

def create_straight_line_approach_simple(
    target_point,
    approach_bearing,
    total_distance,
    num_points=5,
    uav_altitude=80,
):
    approach_waypoints = []
    spacing = (total_distance / (num_points + 1)) * 3
    for i in range(num_points, 0, -1):
        waypoint = new_waypoint(
            target_point[0],
            target_point[1],
            spacing * i,
            (approach_bearing + 180) % 360,
        )
        approach_waypoints.append(
            [waypoint[0], waypoint[1], uav_altitude]
        )

    return approach_waypoints
