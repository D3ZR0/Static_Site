from htmlnode import *
from textnode import *
from textnode import TextType
from blocktype import *
import re

def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
    else:
        raise ValueError(f"Unknown TextType: {text_node.text_type}")
    
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        parts = node.text.split(delimiter)
        if len(parts) %2 == 0:
            raise Exception("invalid markdown syntax, unbalanced delimiter")
        for i, part in enumerate(parts):
            node_type = TextType.TEXT if i %2 == 0 else text_type    
            new_nodes.append(TextNode(part, node_type))
    return new_nodes

    
def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        original_text = node.text
        listed_images = extract_markdown_images(node.text)
        if len(listed_images) == 0:
            new_nodes.append(node)
            continue
        for image in listed_images:
            tuple_text = f"![{image[0]}]({image[1]})"
            sections = original_text.split(tuple_text, 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        original_text = node.text
        listed_links = extract_markdown_links(node.text)
        if len(listed_links) == 0:
            new_nodes.append(node)
            continue
        for j in listed_links:
            tuple_text = f"[{j[0]}]({j[1]})"
            sections = original_text.split(tuple_text, 1)
            if len(sections) != 2:
                raise ValueError("invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(j[0], TextType.LINK, j[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def extract_markdown_links(text):
    listed_matches = []
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    listed_matches.extend(matches)
    return listed_matches

def extract_markdown_images(text):
    listed_matches = []
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    listed_matches.extend(matches)
    return listed_matches

def text_to_textnodes(text):
    original_node = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(original_node)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes

def markdown_to_blocks(markdown):
    markdown_list = markdown.split("\n\n")
    cleaned_list = []
    for block in markdown_list:
        cleaned = block.strip()
        if cleaned == "":
            continue
        cleaned_list.append(cleaned)
    return cleaned_list

def block_to_block_type(block):
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith("#"):
        for n in range(1, 7):
            if block.startswith("#" * n + " "):
                return BlockType.HEADING
    lines = block.split("\n")
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    if all(line.startswith(f"{i+1}. ")for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    return BlockType.PARAGRAPH

def block_to_tag(block):
    blocktype = block_to_block_type(block)
    if blocktype == BlockType.PARAGRAPH:
        return "p"
    if blocktype == BlockType.HEADING:
        count = 0
        for n in block[0: 6]:
            if n == "#":
                count += 1
        return f"h{count}"
    if blocktype == BlockType.CODE:
        return "code"
    if blocktype == BlockType.QUOTE:
        return "blockquote"
    if blocktype == BlockType.UNORDERED_LIST:
        return "ul"
    if blocktype == BlockType.ORDERED_LIST:
        return "ol"
    else:
        raise ValueError("Invalid BLocktype")
    
def text_to_children(text):
    nodes = text_to_textnodes(text)
    leafnodes = []
    for node in nodes:
        leafnode = text_node_to_html_node(node)
        leafnodes.append(leafnode)
    return leafnodes
        

    

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    parentblock = ParentNode("div", children, None)
    for block in blocks:
        bt = block_to_block_type(block)
        tag = block_to_tag(block)
        if bt == BlockType.CODE:
            code_text = "\n".join(block.split("\n")[1:-1])
            child = ParentNode("pre", [LeafNode("code", code_text)])
            children.append(child)
            continue
        if bt == BlockType.HEADING:
            heading_text = block.split(" ", 1)[1]
            child = ParentNode(tag, text_to_children(heading_text))
            children.append(child)
            continue
        if bt == BlockType.QUOTE:
            lines = block.split("\n")
            stripped = []
            for line in lines:
                if line.startswith("> "):
                    stripped.append(line[2:])
                elif line.startswith(">"):
                    stripped.append(line[1:])
                elif line == "":
                    continue
                else:
                    stripped.append(line)
            quote_text = "\n".join(stripped)
            child = ParentNode("blockquote", text_to_children(quote_text))
            children.append(child)
            continue
        
        if bt == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            line_children = []
            stripped = []
            count = 0
            for line in lines:
                count += 1
                if line.startswith(f"{count}. "):
                    new_lines = line.split(" ")
                    stripped.append(new_lines[1])
                elif line.startswith(f"{count}"):
                    new_lines = line.split(".")
                    stripped.append(new_lines[1])
                elif line == "":
                    continue
                else:
                    stripped.append(line)
            for i in stripped:
                child = ParentNode("li", text_to_children(i))
                line_children.append(child)
            parent = ParentNode("ol", line_children)
            children.append(parent)
            continue
        if bt == BlockType.UNORDERED_LIST:
            lines = block.split("\n")
            stripped = []
            line_children = []
            count = 0
            for line in lines:
                count += 1
                if line.startswith("- "):
                    new_lines = line.split(" ")
                    stripped.append(new_lines[1])
                elif line.startswith("-"):
                    new_lines = line.split("-")
                    stripped.append(new_lines[1])
                elif line == "":
                    continue
                else:
                    stripped.append(line)
            for i in stripped:
                child = ParentNode("li", text_to_children(i))
                line_children.append(child)
            parent = ParentNode("ul", line_children)
            children.append(parent)
            continue

        else: 

            child = ParentNode(block_to_tag(block), text_to_children(block))
            children.append(child)
    return parentblock

    
                 
