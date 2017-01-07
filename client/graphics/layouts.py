from lxml import etree
import xmltodict
from io import StringIO
from .colors import Colors
import os
CURR_DIR = os.path.dirname(os.path.abspath(__file__))


class BaseXMLElement(object):
    @classmethod
    def convert(cls, xml_data, parser):
        raise LayoutException("Unimplemented method convert for class %s." % cls.__name__)


class Element(BaseXMLElement):
    def __init__(self, location, size):
        self.location = location
        self.size = size

        self.sprite_data = None
        self.absolute_location = None
        self.absolute_size = None

    def finalize(self, pixel_dimensions, pixel_location=(0, 0)):
        self.absolute_location = pixel_location
        self.absolute_size = pixel_dimensions

    @classmethod
    def convert(cls, xml_data, parser):
        return cls(
            (int(xml_data["@col"]), int(xml_data["@row"])),
            (int(xml_data["@width"]), int(xml_data["@height"]))
        )


class Layout(Element):
    def __init__(self, location, size, dimensions):
        super().__init__(location, size)
        self.children = []
        self.dimensions = dimensions

    def finalize(self, pixel_dimensions, pixel_location=(0, 0)):
        super().finalize(pixel_dimensions, pixel_location)
        grid_size = (pixel_dimensions[0] / self.dimensions[0], pixel_dimensions[1] / self.dimensions[1])
        for child in self.children:
            child_size = (int(grid_size[0] * child.size[0]), int(grid_size[1] * child.size[1]))
            child_location = (int(grid_size[0] * child.location[0]), int(grid_size[1] * child.location[1]))
            child.finalize(child_size, child_location)
        return self

    @classmethod
    def convert(cls, xml_data, parser, depth=0):
        new_layout = Layout(
            (int(xml_data["@col"]), int(xml_data["@row"])),
            (int(xml_data["@width"]), int(xml_data["@height"])),
            (int(xml_data["@cols"]), int(xml_data["@rows"]))
        )

        # convert the children of the layout
        for key in xml_data:
            if key in parser.TAG_MAP:
                xml_element_class = parser.TAG_MAP[key]
                if key in ["element", "layout"]:
                    children_dicts = xml_data[key]
                    if type(children_dicts) != list:
                        children_dicts = [children_dicts]
                    for children_dict in children_dicts:
                        new_layout.children.append(xml_element_class.convert(children_dict, parser))
                if key in ["text-sprite", "color-sprite"]:
                    new_layout.sprite_data = xml_element_class.convert(xml_data[key], parser)

        # validate the children of the layout
        for child in new_layout.children:
            if child.location[0] + child.size[0] > new_layout.size[0] or \
                                    child.location[1] + child.size[1] > new_layout.size[1]:
                raise LayoutException("Child with location %s and size %s exceeds parent's size %s." % (
                    str(child.location),
                    str(child.size),
                    str(new_layout.size)
                ))

        return new_layout


class SpriteData(BaseXMLElement):
    def __init__(self, color, tag):
        self.color = color
        self.tag = tag


class TextSprite(SpriteData):
    def __init__(self, color, tag, text):
        super().__init__(color, tag)
        self.text = text

    @classmethod
    def convert(cls, xml_data, parser):
        tag = xml_data["@tag"] if "@tag" in xml_data else None
        color = Colors.find_color(xml_data["@color"])
        return TextSprite(
            color,
            tag,
            xml_data["@text"]
        )


class ColorSprite(SpriteData):
    def __init__(self, color, tag):
        super().__init__(color, tag)

    @classmethod
    def convert(cls, xml_data, parser):
        tag = xml_data["@tag"] if "@tag" in xml_data else None
        color = Colors.find_color(xml_data["@color"])
        return ColorSprite(
            color,
            tag
        )


class LayoutParser(object):
    SCHEMA = etree.XMLSchema(etree.parse(os.path.join(CURR_DIR, 'layout.xsd')))
    TAG_MAP = {
        "element": Element,
        "layout": Layout,
        "color-sprite": ColorSprite,
        "text-sprite": TextSprite
    }

    @classmethod
    def normalize_root_layout(cls, xml_dict):
        # a root layout doesn't require row, col, height or width
        # because it's assumed it's (0, 0) and (cols, rows) respectively.
        xml_dict["@row"] = 0
        xml_dict["@col"] = 0
        xml_dict["@width"] = xml_dict["@cols"]
        xml_dict["@height"] = xml_dict["@rows"]

    @classmethod
    def generate_layout(cls, filename):
        with open(filename, 'r') as f:
            file_text = f.read()
        doc = etree.parse(StringIO(file_text))
        if not cls.SCHEMA.validate(doc):
            raise LayoutException("XML for %s does not conform to schema." % filename)
        xml_dict = xmltodict.parse(file_text)
        cls.normalize_root_layout(xml_dict["root-layout"])
        return Layout.convert(xml_dict["root-layout"], cls)


class LayoutException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




