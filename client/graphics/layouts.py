from lxml import etree
import xmltodict
from io import StringIO
import os
CURR_DIR = os.path.dirname(os.path.abspath(__file__))


class BaseXMLElement(object):
    @classmethod
    def convert(cls, xml_data, parser):
        raise LayoutException("Unimplemented method convert for class %s." % cls.__name__)


class Container(BaseXMLElement):
    def __init__(self, location, size, tag=None, dimensions=None):
        self.location = location
        self.size = size
        self.tag = tag
        self.dimensions = dimensions if dimensions else (1, 1)

        self.children = []
        self.tagged_containers = {}
        self.depth = None
        self.grid_size = None
        self.absolute_location = None
        self.absolute_size = None

    def add_container(self, child):
        self.children.append(child)

    def container(self, tag):
        if tag not in self.tagged_containers:
            raise LayoutException("Tagged container %s does not exist" % tag)
        return self.tagged_containers[tag]

    def finalize(self, pixel_dimensions, pixel_location=(0, 0), depth=0):
        self.validate()
        self.tagged_containers = {}
        self.absolute_location = pixel_location
        self.absolute_size = pixel_dimensions
        self.depth = depth
        self.grid_size = (pixel_dimensions[0] / self.dimensions[0], pixel_dimensions[1] / self.dimensions[1])

        for child in self.children:
            child_size = (int(self.grid_size[0] * child.size[0]), int(self.grid_size[1] * child.size[1]))
            child_location = (int((self.grid_size[0] * child.location[0]) + self.absolute_location[0]), int((self.grid_size[1] * child.location[1]) + self.absolute_location[1]))
            child.finalize(child_size, child_location, depth=depth+1)

            # if the child has a tag, process it.
            if child.tag:
                if child.tag in self.tagged_containers:
                    raise LayoutException("Duplicate container tag %s found." % child.tag)
                self.tagged_containers[child.tag] = child

            # now process the tagged container keys the child knows of.
            for container_keys in child.tagged_containers.keys():
                if container_keys in self.tagged_containers:
                    raise LayoutException("Duplicate container tag %s found." % container_keys)
                self.tagged_containers[container_keys] = child.tagged_containers[container_keys]

        return self

    def validate(self):
        # validate the children of the layout
        for child in self.children:
            if child.location[0] + child.size[0] > self.dimensions[0] or \
                                    child.location[1] + child.size[1] > self.dimensions[1]:
                raise LayoutException("Child with location %s and size %s exceeds parent's size %s." % (
                    str(child.location),
                    str(child.size),
                    str(self.dimensions)
                ))

    @classmethod
    def convert(cls, xml_data, parser, depth=0):
        tag = xml_data["@tag"] if "@tag" in xml_data and xml_data["@tag"] else None
        dimensions = (int(xml_data["@c"]), int(xml_data["@r"])) if "@c" in xml_data and "@r" in xml_data else None
        location = (int(xml_data["@x"]), int(xml_data["@y"])) if "@x" in xml_data and "@y" in xml_data else(0, 0)
        size = (int(xml_data["@w"]), int(xml_data["@h"])) if "@w" in xml_data and "@h" in xml_data else (1, 1)
        new_layout = Container(
            location,
            size,
            tag=tag,
            dimensions=dimensions
        )

        for key in xml_data.keys():
            if not key.startswith("@"):
                elements = xml_data[key]
                if type(elements) != list:
                    elements = [elements]
                for element in elements:
                    child = Container.convert(element, parser)
                    new_layout.add_container(child)
        return new_layout


class LayoutParser(object):
    SCHEMA = etree.XMLSchema(etree.parse(os.path.join(CURR_DIR, 'layout.xsd')))

    @classmethod
    def normalize_root_container(cls, xml_dict):
        # a root layout doesn't require row, col, height or width
        # because it's assumed it's (0, 0) and (cols, rows) respectively.
        xml_dict["@y"] = 0
        xml_dict["@x"] = 0
        xml_dict["@w"] = xml_dict["@c"]
        xml_dict["@h"] = xml_dict["@r"]

    @classmethod
    def generate_layout(cls, filename):
        with open(filename, 'r') as f:
            file_text = f.read()
        doc = etree.parse(StringIO(file_text))
        if not cls.SCHEMA.validate(doc):
            raise LayoutException("XML for %s does not conform to schema." % filename)
        xml_dict = xmltodict.parse(file_text)["container"]
        cls.normalize_root_container(xml_dict)
        return Container.convert(xml_dict, cls)


class LayoutException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)




