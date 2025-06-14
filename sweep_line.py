from typing import List, Tuple
import heapq

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Segment:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return f"Segment({self.p1}, {self.p2})"

    def __lt__(self, other):
        # Compare segments by their left endpoint's x-coordinate
        # print(f"Comparing {self} < {other}")
        return self.p1.x < other.p1.x or (self.p1.x == other.p1.x and self.p1.y < other.p1.y)


def find_intersections(segments: List[Segment]) -> List[Tuple[Point, Segment, Segment]]:
    events = []
    for seg in segments:
        # Ensure p1 is the left endpoint
        if seg.p1.x > seg.p2.x:
            seg.p1, seg.p2 = seg.p2, seg.p1
        events.append((seg.p1.x, 'left', seg))
        events.append((seg.p2.x, 'right', seg))

    # Sort events by x-coordinate
    heapq.heapify(events)
    copy_events = events.copy()
    sorted_events = []
    while copy_events:
        sorted_events.append(heapq.heappop(copy_events))

    status = []  # Active segments (sorted by y-coordinate at current sweep line)
    intersections = []

    while events:
        x, event_type, seg = heapq.heappop(events)

        if event_type == 'left':
            # Add segment to status and check for intersections with neighbors
            status.append(seg)
            status.sort(key=lambda s: s.p1.y)  # Sort by y-coordinate
            idx = status.index(seg)
            if idx > 0:
                # Check intersection with the segment above
                above = status[idx - 1]
                intersect = find_intersection(seg, above)
                if intersect:
                    intersections.append((intersect, seg, above))
            if idx < len(status) - 1:
                # Check intersection with the segment below
                below = status[idx + 1]
                intersect = find_intersection(seg, below)
                if intersect:
                    intersections.append((intersect, seg, below))
        elif event_type == 'right':
            # Remove segment from status and check for intersections between neighbors
            idx = status.index(seg)
            if idx > 0 and idx < len(status) - 1:
                # Check intersection between the segments above and below
                above = status[idx - 1]
                below = status[idx + 1]
                intersect = find_intersection(above, below)
                if intersect:
                    intersections.append((intersect, above, below))
            status.remove(seg)

    return intersections

def find_intersection(seg1: Segment, seg2: Segment) -> Point:
    # https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect
    # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
    # Calculate intersection point of two line segments (if any)
    x1, y1 = seg1.p1.x, seg1.p1.y
    x2, y2 = seg1.p2.x, seg1.p2.y
    x3, y3 = seg2.p1.x, seg2.p1.y
    x4, y4 = seg2.p2.x, seg2.p2.y

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Parallel or coincident lines as their slopes are equal

    # A line segment can be represented parametrically using two points
    # x = x1 + t(x2 - x1), y = y1 + t(y2-y1)
    # Finding Intersection
    # To find the intersection of two line segments, we solve for t and u such that:
    # x1+t(x2−x1)=x3+u(x4−x3)
    # y1+t(y2−y1)=y3+u(y4−y3)
    # This is playground system of two equations with two unknowns (t and u). Solving this system gives us the values of t and u.
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # parallel lines

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        # intersection point
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        return (px, py)

    return None  # no intersection
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

    if 0 <= t <= 1 and 0 <= u <= 1:
        # Intersection point lies within both segments
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return Point(x, y)
    return None

# Example usage
# segments = [
#     Segment(Point(1, 1), Point(4, 4)),
#     Segment(Point(1, 4), Point(4, 1)),
#     Segment(Point(2, 2), Point(5, 2))
# ]
# Sweep Line Algorithm Implementation
# The sweep line algorithm is a technique used in computational geometry
# to efficiently solve various geometric problems by sweeping a line across the plane

def find_line_intersections(lines):
    """
    Find all intersections between a set of line segments using the sweep line algorithm.

    Time Complexity: O(n log n) where n is the number of line segments
    Space Complexity: O(n)

    Parameters:
        lines (list): List of line segments, each represented as [(x1,y1), (x2,y2)]

    Returns:
        list: List of intersection points (x,y)
    """
    # Event class to represent points of interest (line segment endpoints)
    class Event:
        def __init__(self, x, y, is_start, line_idx):
            self.x = x  # x-coordinate
            self.y = y  # y-coordinate
            self.is_start = is_start  # True if this is the start point of a line segment
            self.line_idx = line_idx  # Index of the line segment this event belongs to

        def __lt__(self, other):
            # Sort by x-coordinate first, then by whether it's a start or end point
            if self.x != other.x:
                return self.x < other.x
            # For same x-coordinate, end points come before start points
            return not self.is_start and other.is_start

    # Helper function to check if two line segments intersect
    def do_lines_intersect(line1, line2):
        # Line 1 coordinates
        x1, y1 = line1[0]
        x2, y2 = line1[1]
        # Line 2 coordinates
        x3, y3 = line2[0]
        x4, y4 = line2[1]

        # Calculate determinants
        det1 = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)

        # If determinant is zero, lines are parallel or collinear
        if det1 == 0:
            return None

        # Calculate intersection point parameters
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / det1
        u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / det1

        # Check if intersection is within both line segments
        if 0 <= t <= 1 and 0 <= u <= 1:
            # Calculate intersection point
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)

        return None

    # Create events for all line segment endpoints
    events = []
    for i, line in enumerate(lines):
        # Ensure the line segment is ordered by x-coordinate
        (x1, y1), (x2, y2) = line
        if x1 > x2 or (x1 == x2 and y1 > y2):
            (x1, y1), (x2, y2) = (x2, y2), (x1, y1)

        # Add start and end events
        events.append(Event(x1, y1, True, i))
        events.append(Event(x2, y2, False, i))

    # Sort events by x-coordinate
    events.sort()

    # Set to keep track of active line segments
    active_lines = set()

    # List to store intersection points
    intersections = []

    # Process events from left to right
    for event in events:
        if event.is_start:
            # For each active line, check for intersection with current line
            for line_idx in active_lines:
                intersection = do_lines_intersect(
                    lines[event.line_idx], lines[line_idx])
                if intersection:
                    intersections.append(intersection)

            # Add current line to active set
            active_lines.add(event.line_idx)
        else:
            # Remove line from active set
            active_lines.remove(event.line_idx)

    return intersections


# Test the algorithm
if __name__ == "__main__":
    # Define some test line segments
    lines = [
        [(0, 0), (10, 10)],    # Line from (0,0) to (10,10)
        [(0, 10), (10, 0)],     # Line from (0,10) to (10,0)
        [(5, 0), (5, 10)],      # Vertical line at x=5
        [(0, 5), (10, 5)]       # Horizontal line at y=5
    ]

    # Find all intersections
    intersections = find_line_intersections(lines)

    print("Line segments:")
    for i, line in enumerate(lines):
        print(f"Line {i}: {line}")

    print("\nIntersections:")
    for i, point in enumerate(intersections):
        print(f"Intersection {i}: ({point[0]:.2f}, {point[1]:.2f})")
segments = [
    Segment(Point(1, 3), Point(5, 1)),
    Segment(Point(2, 2), Point(4, 4)),
    Segment(Point(3, 0), Point(6, 3))
]

intersections = find_intersections(segments)
for intersect, seg1, seg2 in intersections:
    print(f"Intersection at {intersect} between {seg1} and {seg2}")