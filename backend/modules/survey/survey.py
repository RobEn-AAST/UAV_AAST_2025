from ..utils import get_bearing_2_points, new_waypoint, get_dist_2_points
from ..survey.rect_points import RectPoints
from ..config import MissionConfig

def generateSurveyFromList(search_list: list[list[float]], spacing, planeLocation) -> list[list[float]]:
    if len(search_list) != 4:
        raise ValueError("Search grid must have 4 points to form a rectangle")
        
    searchRec = RectPoints(*search_list)
    return generateSurveyFromRect(searchRec, spacing, planeLocation)

def generateSurveyFromRect(search_rect: RectPoints, spacing, planeLocation) -> list[list[float]]:
    points = []
    closestPoint = search_rect.getClosestPoint(planeLocation)
    furthestConnectedPoint = search_rect.getFurthestConnectedPoint(closestPoint)

    travelBearing = get_bearing_2_points(*closestPoint, *furthestConnectedPoint)
    travelDistance = get_dist_2_points(*closestPoint, *furthestConnectedPoint)

    rotatePoint2 = [point for point in search_rect.getConnectedPoints(furthestConnectedPoint) if point != closestPoint][0]
    rotateBearing = get_bearing_2_points(*furthestConnectedPoint, *rotatePoint2)
    uncoveredDistance = get_dist_2_points(*furthestConnectedPoint, *rotatePoint2)

    lastPoint = closestPoint
    rotateToggle = False
    direction = 0

    while uncoveredDistance > 0:
        points.append([lastPoint[0], lastPoint[1], MissionConfig.survey_alt])

        if rotateToggle:
            lastPoint = new_waypoint(*lastPoint, spacing, rotateBearing)
            uncoveredDistance -= spacing
            direction += 180
            rotateToggle = False
        else:
            lastPoint = new_waypoint(*lastPoint, travelDistance, travelBearing + direction)
            rotateToggle = True

    return points