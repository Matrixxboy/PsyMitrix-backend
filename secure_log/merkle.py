# secure_log/merkle.py
# Core logic for building a Merkle Tree.

import hashlib

# Point-wise comment: A node in the Merkle Tree
class Node:
    def __init__(self, left, right, value: str, content: str, is_leaf=False):
        self.left = left
        self.right = right
        self.value = value
        self.content = content
        self.is_leaf = is_leaf

    @staticmethod
    def hash(val: str) -> str:
        return hashlib.sha256(val.encode('utf-8')).hexdigest()

# Point-wise comment: A leaf node in the Merkle Tree, representing a single log entry
class Leaf(Node):
    def __init__(self, content: str):
        value = self.hash(content)
        super().__init__(None, None, value, content, is_leaf=True)

# Point-wise comment: Build the Merkle Tree from a list of leaf nodes
def build_merkle_tree(leaves: list[Node]) -> Node:
    num_leaves = len(leaves)
    if num_leaves == 1:
        return leaves[0]

    parents = []
    i = 0
    while i < num_leaves:
        left_child = leaves[i]
        right_child = leaves[i + 1] if i + 1 < num_leaves else left_child
        
        parent_value = Node.hash(left_child.value + right_child.value)
        parent_content = left_child.content + ' | ' + right_child.content
        parents.append(Node(left_child, right_child, parent_value, parent_content))
        
        i += 2
        
    return build_merkle_tree(parents)
