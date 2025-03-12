from pyproj import Proj, transform

def latlon_to_xy(lat, lon, zone_number=None, northern=True):
    """
    Convert latitude and longitude (in degrees) to UTM coordinates (in meters).

    Parameters:
      lat (float): latitude in degrees
      lon (float): longitude in degrees
      zone_number (int, optional): UTM zone number. If not provided, it is calculated from longitude.
      northern (bool, optional): True for northern hemisphere, False for southern hemisphere.

    Returns:
      (x, y): UTM easting and northing in meters.
    """
    if zone_number is None:
        zone_number = int((lon + 180) / 6) + 1

    proj_latlon = Proj(proj='latlong', datum='WGS84')
    proj_utm = Proj(proj='utm', zone=zone_number, datum='WGS84', south=not northern)

    x, y = transform(proj_latlon, proj_utm, lon, lat)
    return x, y, zone_number


def xy_to_latlon(x, y, zone_number, northern=True):
    """
    Convert UTM coordinates (in meters) to latitude and longitude (in degrees).

    Parameters:
      x (float): UTM easting in meters.
      y (float): UTM northing in meters.
      zone_number (int): UTM zone number.
      northern (bool, optional): True for northern hemisphere, False for southern hemisphere.

    Returns:
      (lat, lon): Latitude and longitude in degrees.
    """
    proj_utm = Proj(proj='utm', zone=zone_number, datum='WGS84', south=not northern)

    lon, lat = proj_utm(x, y, inverse=True)
    return lat, lon


if __name__ == '__main__':
    lat = -35.3625567
    lon = 149.1651696
    x, y, zone = latlon_to_xy(lat, lon)

    new_lat, new_lon = xy_to_latlon(x, y, zone)
    print(new_lat - lat, new_lon - lon)
