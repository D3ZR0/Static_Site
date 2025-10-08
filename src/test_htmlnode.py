import unittest

from htmlnode import *

class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode("div", None, None, {"id": "main"})
        expected_repr = "HTMLNode(tag = div, value = None, children = None, props = {'id': 'main'})"
        self.assertEqual(repr(node), expected_repr)
    
    def test_props_to_html_none(self):
        node = HTMLNode("div", None, None, None)
        self.assertEqual(node.props_to_html(), "")
    
    def test_props_to_html_with_props(self):
        node = HTMLNode("div", None, None, {"class": "container", "id": "main"})
        self.assertEqual(node.props_to_html(), ' class="container" id="main"')

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_span_with_props(self):
        node = LeafNode("a", "Click me!", {"href": "http://example.com"})
        self.assertEqual(node.to_html(), '<a href="http://example.com">Click me!</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )