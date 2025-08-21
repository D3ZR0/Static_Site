import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)
    
    def test_repr(self):
        node = TextNode("Sample Text", TextType.BOLD)
        expected_repr = "TextNode(Sample Text, BOLD, None)"
        self.assertEqual(repr(node), expected_repr)

    def test_repr_with_url(self):
        node = TextNode("Sample Link", TextType.LINK, "http://example.com")
        expected_repr = "TextNode(Sample Link, LINK, http://example.com)"
        self.assertEqual(repr(node), expected_repr)
    
    def test_repr_with_image(self):
        node = TextNode("Sample Image", TextType.IMAGE, "http://example.com/image.png")
        expected_repr = "TextNode(Sample Image, IMAGE, http://example.com/image.png)"
        self.assertEqual(repr(node), expected_repr)


if __name__ == "__main__":
    unittest.main()