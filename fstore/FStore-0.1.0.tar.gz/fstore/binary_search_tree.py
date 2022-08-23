from collections import deque

# Create a node
class Node:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.left = None
        self.right = None

# Search by key
def search(root, key):
    if not root:
        return
    if key < root.key:
        return search(root.left, key)
    elif key > root.key:
        return search(root.right, key)
    else:
        return root.val

# Insert a node
def insert(root, key, val):

    # Return a new node if the tree is empty
    if not root:
        return Node(key, val)

    # Traverse to the right place and insert the node
    if key < root.key:
        root.left = insert(root.left, key, val)
    else:
        root.right = insert(root.right, key, val)

    return root

# Find the inorder successor
def inorder_successor(root):
    current = root

    while(current.left):
        current = current.left

    return current

# Delete node
def delete(root, key):
    # Key is not in tree
    if not root:
        return root

    # Find the node to be deleted
    if key < root.key:
        root.left = delete(root.left, key)
    elif(key > root.key):
        root.right = delete(root.right, key)
    else:
        # If the node is with only one child or no child
        if root.left is None:
            temp = root.right
            root = None
            return temp

        elif root.right is None:
            temp = root.left
            root = None
            return temp

        # If the node has two children,
        # place the inorder successor in position of the node to be deleted
        temp = inorder_successor(root.right)

        root.key = temp.key

        # Delete the inorder successor
        root.right = delete(root.right, temp.key)

    return root

# Serialize tree to string
def serialize(root):
    if not root:
        return ""
    
    result = ""
    q = deque()
    q.append(root)
    while len(q) > 0:
        cur = q.popleft()
        if cur:
            result += str(cur.key) + ":" + str(cur.val)
            if cur.left:
                q.append(cur.left)
            else:
                q.append(None)
            if cur.right:
                q.append(cur.right)
            else:
                q.append(None)
        else:
            result += "NULL:NULL"
        result += ","
    
    return result

# Deserialize tree from string
def deserialize(string):
    # Parse string into array of strings
    tmp = string.split(",")
    data = []

    for i in range(len(tmp)-1):
        # Separate strings into key-value pairs
        data.append(tmp[i].split(":"))

    return make(data)

# Make tree from array of key-value pairs
def make(elements):
    root = None

    for element in elements:
        key = element[0]
        val = element[1]

        # Skip over null nodes
        if key != "NULL":
            root = insert(root, key, val)
        
    return root
