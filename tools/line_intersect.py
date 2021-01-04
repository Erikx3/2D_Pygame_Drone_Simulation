import numpy as np

# https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines


def line_intersection(line1, line2):
    """

    :param line1: line defined by two points, e.g. [[1,1], [2,2]]
    :param line2: second line
    :return: point of intersection,
    """

    # Functions to check, whether line intersect at all:
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    # Return true if line segments AB and CD intersect
    def intersect(A, B, C, D):
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    if intersect(line1[0], line1[1], line2[0], line2[1]):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        # Fallback, if intersect did not work
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return [x, y]
    else:
        return None


def distance(p1, p2):
    """

    :param p1: point, e.g. [1,2]
    :param p2: second point
    :return: distance between these two points
    """
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1]-p1[1])**2)
