import math

def lat_lon_to_cartesian(lat, lon, R=6371):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    x = R * math.cos(lat_rad) * math.cos(lon_rad)
    y = R * math.cos(lat_rad) * math.sin(lon_rad)
    z = R * math.sin(lat_rad)
    return x, y, z


def cartesian_to_lat_lon(x, y, z):

    R = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    lat = math.degrees(math.asin(z / R))
    lon = math.degrees(math.atan2(y, x))
    return lat, lon


def project_point_on_great_circle(lat1, lon1, lat2, lon2, lat3, lon3):

    # Convert all points to Cartesian coordinates
    x1, y1, z1 = lat_lon_to_cartesian(lat1, lon1)
    x2, y2, z2 = lat_lon_to_cartesian(lat2, lon2)
    x3, y3, z3 = lat_lon_to_cartesian(lat3, lon3)

    # Compute the normal vector of the plane of the great circle
    N_x = y1 * z2 - z1 * y2
    N_y = z1 * x2 - x1 * z2
    N_z = x1 * y2 - y1 * x2

    # Normalize the normal vector
    N_mag = math.sqrt(N_x ** 2 + N_y ** 2 + N_z ** 2)
    N_x /= N_mag
    N_y /= N_mag
    N_z /= N_mag

    # Project the external point onto the plane
    dot_product = x3 * N_x + y3 * N_y + z3 * N_z
    x_proj = x3 - dot_product * N_x
    y_proj = y3 - dot_product * N_y
    z_proj = z3 - dot_product * N_z

    # Convert the projected Cartesian coordinates back to lat/lon
    lat_proj, lon_proj = cartesian_to_lat_lon(x_proj, y_proj, z_proj)

    return lat_proj, lon_proj


