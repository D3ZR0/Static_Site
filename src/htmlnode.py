

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
