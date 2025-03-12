from typing import List
from modules.utils import get_dist_2_points


class RectPoints:
    def __init__(self, p1: List[float], p2: List[float], p3: List[float], p4: List[float]):
        cords = [p1, p2, p3, p4]
        sortedByLat = sorted(cords, key=lambda x: x[0])

        if sortedByLat[0][1] < sortedByLat[1][1]:
            self.bottomLeft = sortedByLat[0][:2]
            self.bottomRight = sortedByLat[1][:2]
        else:
            self.bottomLeft = sortedByLat[1][:2]
            self.bottomRight = sortedByLat[0][:2]

        if sortedByLat[2][1] < sortedByLat[3][1]:
            self.topLeft = sortedByLat[2][:2]
            self.topRight = sortedByLat[3][:2]
        else:
            self.topLeft = sortedByLat[3][:2]
            self.topRight = sortedByLat[2][:2]

        self.length = get_dist_2_points(self.topRight[0], self.topRight[1], self.bottomRight[0], self.bottomRight[1])
        self.width = get_dist_2_points(self.topRight[0], self.topRight[1], self.topLeft[0], self.topLeft[1])

    def getClosestPoint(self, location: List[float]) -> List[float]:
        closestPoint = self.topLeft
        closestDistance = get_dist_2_points(self.topLeft[0], self.topLeft[1], location[0], location[1])

        points = [self.topRight, self.bottomRight, self.bottomLeft]

        for point in points:
            distanceToPoint = get_dist_2_points(point[0], point[1], location[0], location[1])
            if distanceToPoint < closestDistance:
                closestPoint = point
                closestDistance = distanceToPoint

        return closestPoint

    def getConnectedPoints(self, point: List[float]) -> List[float]:
        if point == self.topLeft:
            return [self.topRight, self.bottomLeft]
        elif point == self.topRight:
            return [self.topLeft, self.bottomRight]
        elif point == self.bottomRight:
            return [self.topRight, self.bottomLeft]
        elif point == self.bottomLeft:
            return [self.topLeft, self.bottomRight]

    def getFurthestConnectedPoint(self, location: List[float]) -> List[float]:
        furthestPoint = None
        furthestDistance = 0

        for point in self.getConnectedPoints(location):
            distanceToPoint = get_dist_2_points(*point, *location)
            if distanceToPoint > furthestDistance:
                furthestPoint = point
                furthestDistance = distanceToPoint

        return furthestPoint