from htmlnode import *
from textnode import *
from textnode import TextType
from blocktype import *
import re
import os

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
            new_nodes.append(node); continue

        parts = node.text.split(delimiter)
        count = len(parts) - 1  # delimiter occurrences

        if count == 0:
            new_nodes.append(node); continue

        if count % 2 == 1:
            # unmatched single opener: raise (this satisfies the test)
            raise Exception("invalid markdown syntax, unbalanced delimiter")

        # balanced: alternate plain/formatted
        for i, part in enumerate(parts):
            if part == "":
                continue
            node_type = text_type if (i % 2 == 1) else TextType.TEXT
            new_nodes.append(TextNode(part, node_type))
    return new_nodes

    
def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node); continue
        text = node.text
        imgs = extract_markdown_images(text)
        if not imgs:
            new_nodes.append(node); continue
        for alt, src in imgs:
            token = f"![{alt}]({src})"
            before, sep, after = text.partition(token)
            if not sep:
                # not found as literal; bail out as plain
                new_nodes.append(TextNode(text, TextType.TEXT))
                text = ""
                break
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt, TextType.IMAGE, src))
            text = after
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node); continue
        text = node.text
        links = extract_markdown_links(text)
        if not links:
            new_nodes.append(node); continue
        for label, href in links:
            token = f"[{label}]({href})"
            before, sep, after = text.partition(token)
            if not sep:
                new_nodes.append(TextNode(text, TextType.TEXT))
                text = ""
                break
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(label, TextType.LINK, href))
            text = after
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))
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
    parentblock = ParentNode("div", children)
    for block in blocks:
        bt = block_to_block_type(block)
        if bt == BlockType.CODE:
            lines = block.split("\n")
            inner = "\n".join(lines[1:-1])
            if not inner.endswith("\n"):
                inner += "\n"
            children.append(ParentNode("pre", [LeafNode("code", inner)]))
            continue
        if bt == BlockType.HEADING:
            heading_text = block.split(" ", 1)[1]
            count = len(block) - len(block.lstrip("#"))
            children.append(ParentNode(f"h{count}", text_to_children(heading_text)))
            continue
        if bt == BlockType.QUOTE:
            lines = block.split("\n")
            stripped = []
            for line in lines:
                if line.startswith("> "):
                    stripped.append(line[2:])
                elif line.startswith(">"):
                    stripped.append(line[1:])
                elif line:
                    stripped.append(line)
            quote_text = "\n".join(stripped)
            children.append(ParentNode("blockquote", text_to_children(quote_text)))
            continue
        
        if bt == BlockType.ORDERED_LIST:
            lines = block.split("\n")
            line_children = []
            stripped = []
            count = 0
            for line in lines:
                count += 1
                if line.startswith(f"{count}. "):
                    new_lines = line.split(" ", 1)
                    stripped.append(new_lines[1])
                elif line.startswith(f"{count}"):
                    new_lines = line.split(".", 1)
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
                    new_lines = line.split(" ", 1)
                    stripped.append(new_lines[1])
                elif line.startswith("-"):
                    new_lines = line.split("-", 1)
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
        if bt == BlockType.PARAGRAPH:
            para_text = " ".join(ln.strip() for ln in block.split("\n") if ln.strip())
            children.append(ParentNode("p", text_to_children(para_text)))
    return parentblock
    
                 
def extract_title(markdown):
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        if block_to_tag(block) == "h1":
                line = block.lstrip()
                header_text = line.split("#", 1)[1]
                return header_text.strip()
    raise Exception("No Header 1 detected")

def generate_page(from_path, template_path, dest_path):
    if not os.path.exists(from_path):
        raise FileNotFoundError(f"Source not found: {from_path}")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, 'r', encoding='utf-8') as f:
        page_text = f.read()
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    nodes = markdown_to_html_node(page_text)
    html_page = nodes.to_html()
    title = extract_title(page_text)
    final_html = template.replace("{{ Title }}", title).replace("{{ Content }}", html_page)
    parent = os.path.dirname(dest_path)    
    if parent != "":
        os.makedirs(parent, exist_ok = True)
    with open(dest_path, 'w', encoding="utf-8") as f:
        f.write(final_html)

