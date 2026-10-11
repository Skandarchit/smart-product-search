"""A category forest: each path has three levels, with no extra root level."""
from dataclasses import dataclass, field


@dataclass
class CategoryNode:
    name: str
    children: list["CategoryNode"] = field(default_factory=list)


def build_hierarchy(products):
    roots = []
    for product in products:
        siblings = roots
        for label in product.category:
            node = next((n for n in siblings if n.name == label), None)
            if node is None:
                node = CategoryNode(label)
                siblings.append(node)
            siblings = node.children
    return roots


def preorder(roots, depth=0):
    for node in roots:
        yield depth, node.name
        yield from preorder(node.children, depth + 1)


def diagram(products):
    return "\n".join("    " * depth + "- " + name
                     for depth, name in preorder(build_hierarchy(products)))
