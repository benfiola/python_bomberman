from lxml import etree
import xmltodict
from io import StringIO
import client.graphics.colors as colors


class XMLElement(object):
    @classmethod
    def get_element_name(cls):
        raise LayoutException("Unimplemented method get_key for class %s." % cls.__name__)

    @classmethod
    def from_xml_dict(cls, xml_dict, **kwargs):
        raise LayoutException("Unimplemented method from_xml_dict for class %s." % cls.__name__)


class SpriteData(XMLElement):
    def __init__(self, color, tag):
        self.tag = tag
        self.color = color


class ColorSpriteData(SpriteData):
    def __init__(self, color, tag=None):
        super().__init__(color, tag)

    @classmethod
    def from_xml_dict(cls, xml_dict, **kwargs):
        color = getattr(colors.Colors, xml_dict["@color"].upper(), None)
        if color is None:
            raise LayoutException("Unrecognized color %s." % xml_dict["@color"])
        tag = xml_dict["@tag"] if "@tag" in xml_dict else None
        return ColorSpriteData(
            color,
            tag
        )

    @classmethod
    def get_element_name(cls):
        return "color-sprite"


class TextSpriteData(SpriteData):
    def __init__(self, color, text, tag=None):
        super().__init__(color, tag)
        self.text = text

    @classmethod
    def from_xml_dict(cls, xml_dict, **kwargs):
        tag = xml_dict["@tag"] if "@tag" in xml_dict else None
        color = getattr(colors.Colors, xml_dict["@color"].upper(), None)
        if not color:
            raise LayoutException("Unrecognized color %s." % xml_dict["@color"])
        return TextSpriteData(
            color,
            tag,
            xml_dict["@text"]
        )

    @classmethod
    def get_element_name(cls):
        return "text-sprite"


class Element(XMLElement):
    def __init__(self, depth, location, size):
        self.depth = depth
        self.location = location
        self.size = size
        self.absolute_location = None
        self.absolute_size = None
        self.sprite_data = None

    @classmethod
    def from_xml_dict(cls, xml_dict, depth=0):

        return Element(
            depth,
            (int(xml_dict["@col"]), int(xml_dict["@row"])),
            (int(xml_dict["@width"]), int(xml_dict["@height"])),
        )

    @classmethod
    def get_element_name(cls):
        return "element"


class Layout(Element):
    def __init__(self, depth, location, size, dimensions):
        super().__init__(depth, location, size)
        self.dimensions = dimensions
        self.children = []

    def finalize(self, screen_dimensions):
        pass

    @classmethod
    def from_xml_dict(cls, xml_dict, depth=0):
        sprite_data = None
        if "text-sprite" in xml_dict:
            sprite_data = TextSpriteData.from_xml_dict(xml_dict["text-sprite"])
        elif "color-sprite" in xml_dict:
            sprite_data = ColorSpriteData.from_xml_dict(xml_dict["color-sprite"])

        # at 0 depth, we're expecting a root layout - this means it doesn't have
        # it's going to be positioned at 0, 0 and takes up the whole screenspace.
        if depth == 0:
            new_layout = Layout(
                depth,
                (0, 0),
                (int(xml_dict["@cols"]), int(xml_dict["@rows"])),
                (int(xml_dict["@cols"]), int(xml_dict["@rows"])),
                sprite_data=sprite_data
            )
        else:
            new_layout = Layout(
                depth,
                (int(xml_dict["@col"]), int(xml_dict["@row"])),
                (int(xml_dict["@width"]), int(xml_dict["@height"])),
                (int(xml_dict["@cols"]), int(xml_dict["@rows"])),
                sprite_data=sprite_data
            )
        if "element" in xml_dict:
            new_layout.children.extend([super(Layout, cls).from_xml_dict(element_dict, depth=depth+1) for element_dict in xml_dict["element"]])
        if "layout" in xml_dict:
            new_layout.children.extend([cls.from_xml_dict(layout_dict, depth=depth+1) for layout_dict in xml_dict["layout"]])

        # lets validate our direct children
        for child in new_layout.children:
            if child.location[0] + child.size[0] >= new_layout.size[0] or child.location[1] + child.size[1] >= new_layout.size[1]:
                raise Exception("Child element exceeds layout size of parent.")
        return new_layout

class LayoutParser(object):
    schema = etree.XMLSchema(etree.parse('layout.xsd'))

    @classmethod
    def generate_layout(cls, filename):
        with open(filename, 'r') as f:
            file_text = f.read()
        doc = etree.parse(StringIO(file_text))
        if not cls.schema.validate(doc):
            raise Exception("XML for %s does not conform to schema." % filename)
        xml_dict = xmltodict.parse(file_text)
        return Layout.from_xml_dict(xml_dict["root-layout"])


class LayoutException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

import client
root_layout = LayoutParser.generate_layout('layout.xml')
print("here")




