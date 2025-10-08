

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
        if self.value is None:
            raise ValueError("LeafNodes must have a value")
        if self.tag is None:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
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
            raise ValueError("ParentNodes must have a tag")
        if self.children is None:
            raise ValueError("ParentNodes must have children")
        return f"<{self.tag}{self.props_to_html()}>{self.children_to_html()}</{self.tag}>"
    
    
