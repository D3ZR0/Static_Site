import unittest
from functions import *
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType
from blocktype import *

class TestConverters(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    
    def test_bold(self):
        node = TextNode("This is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold text")
    
    def test_italic(self):
        node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic text")

    def test_code(self):
        node = TextNode("print('Hello, world!')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello, world!')")
    
    def test_link(self):
        node = TextNode("OpenAI", TextType.LINK, "https://www.openai.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "OpenAI")
        self.assertEqual(html_node.props, {"href": "https://www.openai.com"})
    
    def test_split_nodes_delimiter_bold(self):
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))

    def test_split_nodes_delimiter_italic(self):
        nodes = [TextNode("This is *italic* text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("italic", TextType.ITALIC))
        self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))
    
    def test_split_nodes_delimiter_unbalanced(self):
        nodes = [TextNode("This is **bold text", TextType.TEXT)]
        with self.assertRaises(Exception) as context:
            split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertTrue("invalid markdown syntax, unbalanced delimiter" in str(context.exception))
    
    def test_split_nodes_delimiter_multiple(self):
        nodes = [TextNode("This is **bold** and *italic* text", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 5)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(new_nodes[2], TextNode(" and ", TextType.TEXT))
        self.assertEqual(new_nodes[3], TextNode("italic", TextType.ITALIC))
        self.assertEqual(new_nodes[4], TextNode(" text", TextType.TEXT))
    
    def test_split_node_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("This is **bold** text", TextType.TEXT),
            TextNode("Another *italic* text", TextType.TEXT)
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertEqual(len(new_nodes), 6)
        self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))
        self.assertEqual(new_nodes[3], TextNode("Another ", TextType.TEXT))
        self.assertEqual(new_nodes[4], TextNode("italic", TextType.ITALIC))
        self.assertEqual(new_nodes[5], TextNode(" text", TextType.TEXT))

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is a text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", TextType.TEXT, 
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is a text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ], 
            new_nodes, 
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        textnodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            textnodes,
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_block_type_code(self):
        text = "``` this is a code block```"
        result = block_to_block_type(text)
        self.assertEqual(BlockType.CODE, result)

    def test_block_to_block_type_heading_bad(self):
        text = "###badheading"
        result = block_to_block_type(text)
        self.assertEqual(BlockType.PARAGRAPH, result)
    
    def test_block_to_block_type_heading(self):
        text = "#### a real heading"
        result = block_to_block_type(text)
        self.assertEqual(BlockType.HEADING, result)

    def test_block_to_block_type_multiquote(self):
        text = """> chicken
> is 
> amazing"""
        result = block_to_block_type(text)
        self.assertEqual(BlockType.QUOTE, result)

    def test_block_to_block_type_ordered_list(self):
        text = """1. chicken
2. is 
3. love"""
        result = block_to_block_type(text)
        self.assertEqual(BlockType.ORDERED_LIST, result)

    def test_block_to_block_type_unordered_list(self):
        text = """- i  
- am 
- not 
- a 
- chicken"""
        result = block_to_block_type(text)
        self.assertEqual(BlockType.UNORDERED_LIST, result)

    def test_block_to_block_type_paragraph(self):
        text = """- i 
- am 
actually a paragraph"""
        result = block_to_block_type(text)
        self.assertEqual(BlockType.PARAGRAPH, result)

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
            )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
        "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )    
    
    def test_extract_title(self):
        markdown = "# This is a header"
        title = extract_title(markdown)
        self.assertEqual(title, "This is a header")

    def test_extract_title_error(self):
        markdown = "Hello"
        with self.assertRaises(Exception):
            extract_title(markdown)

    def test_extract_title_error_h2(self):
        markdown = "## Hello"
        with self.assertRaises(Exception):
            extract_title(markdown)
