# Python example of Floyd’s Cycle Detection (Tortoise and Hare) of Single-Linked List data structure

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

def has_cycle(head):
    slow = head      # Start both pointers at the head
    fast = head
    while fast and fast.next:
        slow = slow.next         # Moves 1 step
        fast = fast.next.next    # Moves 2 steps
        if slow == fast:
            return True          # Cycle detected
    return False                 # No cycle

# Example usage:
# Create nodes
a = Node('A')
b = Node('B')
c = Node('C')
d = Node('D')

# Create a cycle: A -> B -> C -> D -> B (cycle back to B)
a.next = b
b.next = c
c.next = d
d.next = b

print(has_cycle(a))  # Output: True

# Create a non-cyclic list: A -> B -> C -> D -> None
d.next = None

print(has_cycle(a))  # Output: False