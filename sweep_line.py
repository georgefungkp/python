# Sweep Line Algorithm Implementation for Finding Line Segment Intersections
# This module implements the sweep line algorithm, which is an efficient technique
# for finding intersections among a set of line segments in a plane.
# Time Complexity: O(n log n) where n is the number of line segments
# Space Complexity: O(n)

from typing import List, Tuple
import heapq

class Point:
    """Represents a 2D point with x and y coordinates."""
    def __init__(self, x, y):
        self.x = x  # x-coordinate
        self.y = y  # y-coordinate

    def __repr__(self):
        """String representation of the point."""
        return f"({self.x}, {self.y})"

class Segment:
    """Represents a line segment defined by two endpoints."""
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1  # First endpoint
        self.p2 = p2  # Second endpoint

    def __repr__(self):
        """String representation of the segment."""
        return f"Segment({self.p1}, {self.p2})"

    def __lt__(self, other):
        """Comparison operator for sorting segments.

        Segments are compared by their left endpoints' x-coordinates,
        with y-coordinate as a tiebreaker.
        """
        return self.p1.x < other.p1.x or (self.p1.x == other.p1.x and self.p1.y < other.p1.y)


def find_intersections(segments: List[Segment]) -> List[Tuple[Point, Segment, Segment]]:
    """Find all intersections between line segments using the sweep line algorithm.

    The sweep line algorithm works by:
    1. Creating events for each segment's endpoints (left and right)
    2. Processing events from left to right
    3. Maintaining a status structure of active segments at the current sweep line position
    4. Checking for intersections between adjacent segments in the status structure

    Args:
        segments: List of line segments to check for intersections

    Returns:
        List of tuples, each containing an intersection point and the two segments that intersect
    """
    # Create events for each segment's endpoints
    events = []
    for seg in segments:
        # Ensure p1 is the left endpoint (has smaller x-coordinate)
        if seg.p1.x > seg.p2.x:
            seg.p1, seg.p2 = seg.p2, seg.p1
        # Add left and right endpoint events to the queue
        events.append((seg.p1.x, 'left', seg))   # Left endpoint event
        events.append((seg.p2.x, 'right', seg))  # Right endpoint event

    # Use a priority queue to sort events by x-coordinate
    heapq.heapify(events)  # Convert events list to a min-heap

    # Create a sorted copy of events (for debugging/visualization purposes)
    copy_events = events.copy()
    sorted_events = []
    while copy_events:
        sorted_events.append(heapq.heappop(copy_events))

    # Status line - stores active segments intersecting the current sweep line
    # Segments in status are sorted by their y-coordinate at the sweep line
    status = []  

    # List to store all found intersections
    intersections = []

    # Process events from left to right (increasing x-coordinate)
    while events:
        # Get the next event (leftmost x-coordinate)
        x, event_type, seg = heapq.heappop(events)

        if event_type == 'left':
            # Left endpoint event: segment enters the sweep line

            # Add segment to status
            status.append(seg)
            # Sort status by y-coordinate at the current sweep line position
            status.sort(key=lambda s: s.p1.y)  

            # Find the position of the new segment in the sorted status
            idx = status.index(seg)

            # Check for intersection with the segment above (if exists)
            if idx > 0:
                above = status[idx - 1]
                intersect = find_intersection(seg, above)
                if intersect:
                    intersections.append((intersect, seg, above))

            # Check for intersection with the segment below (if exists)
            if idx < len(status) - 1:
                below = status[idx + 1]
                intersect = find_intersection(seg, below)
                if intersect:
                    intersections.append((intersect, seg, below))

        elif event_type == 'right':
            # Right endpoint event: segment leaves the sweep line

            # Find the position of the segment in the status
            idx = status.index(seg)

            # When removing a segment, check if its neighbors might intersect
            if idx > 0 and idx < len(status) - 1:
                # Get segments above and below the one being removed
                above = status[idx - 1]
                below = status[idx + 1]

                # Check if these two segments intersect
                intersect = find_intersection(above, below)
                if intersect:
                    intersections.append((intersect, above, below))

            # Remove the segment from status
            status.remove(seg)

    return intersections


def find_intersection(seg1: Segment, seg2: Segment) -> Point:
    """Calculate the intersection point of two line segments if they intersect.

    This function uses the parametric form of line equations to find the intersection.
    References:
    - https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect
    - https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

    Args:
        seg1: First line segment
        seg2: Second line segment

    Returns:
        The intersection point if segments intersect, None otherwise
    """
    # Extract coordinates of the endpoints
    x1, y1 = seg1.p1.x, seg1.p1.y  # First endpoint of segment 1
    x2, y2 = seg1.p2.x, seg1.p2.y  # Second endpoint of segment 1
    x3, y3 = seg2.p1.x, seg2.p1.y  # First endpoint of segment 2
    x4, y4 = seg2.p2.x, seg2.p2.y  # Second endpoint of segment 2

    # Calculate the denominator of the equations
    # If denominator is 0, lines are parallel or collinear
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # Parallel or coincident lines as their slopes are equal

    # Calculate parameters t and u
    # A line segment can be represented parametrically as:
    # Point on segment 1: (x,y) = (x1,y1) + t*(x2-x1,y2-y1) where 0 ≤ t ≤ 1
    # Point on segment 2: (x,y) = (x3,y3) + u*(x4-x3,y4-y3) where 0 ≤ u ≤ 1
    # At intersection point, these two equations are equal, forming a system:
    # x1 + t(x2-x1) = x3 + u(x4-x3)
    # y1 + t(y2-y1) = y3 + u(y4-y3)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = ((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2)) / denom

    # If both t and u are between 0 and 1, segments intersect
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate the intersection point using parameter t
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        return Point(px, py)

    # If t or u is outside [0,1], segments don't intersect
    return None


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

    # Test with Point and Segment classes
    segments = [
        Segment(Point(1, 3), Point(5, 1)),
        Segment(Point(2, 2), Point(4, 4)),
        Segment(Point(3, 0), Point(6, 3))
    ]

    intersections = find_intersections(segments)
    for intersect, seg1, seg2 in intersections:
        print(f"Intersection at {intersect} between {seg1} and {seg2}")