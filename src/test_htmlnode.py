import unittest

from htmlnode import HTMLNode

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