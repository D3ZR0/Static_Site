

class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError("Subclasses must implement to_html method")

    def props_to_html(self):
        if self.props is None:
            return ""
        else: 
            string = ""
            keys = sorted(self.props.keys())
            for i in keys:
                string += f' {i}="{self.props[i]}"'
            return string
    
    def __repr__(self):
        return f"HTMLNode(tag = {self.tag}, value = {self.value}, children = {self.children}, props = {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag =  None, value = None, props = None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if self.tag is None:
            return self.value or ""
        attrs = "" if not self.props else " " + " ".join(f'{k}="{v}"' for k,v in self.props.items())
        return f"<{self.tag}{attrs}>{self.value or ''}</{self.tag}>"
    
class ParentNode(HTMLNode):
    def __init__(self, tag = None, children = None, props = None):
        super().__init__(tag, None, children, props)
    
    def children_to_html(self):
        if self.children is None:
            return ""
        html = ""
        for child in self.children:
            html += child.to_html()
            return html
        
    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        inner = "".join(child.to_html() for child in self.children or [])
        attrs = "" if not self.props else " " + " ".join(f'{k}="{v}"' for k,v in self.props.items())
        return f"<{self.tag}{attrs}>{inner}</{self.tag}>"
    
    
