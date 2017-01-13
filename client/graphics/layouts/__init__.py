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
    def __init__(self, location, size, tag=None, dimensions=None, depth=None):
        self.location = location
        self.size = size
        self.tag = tag
        self.dimensions = dimensions if dimensions else (1, 1)
        self.depth = depth
        self.children = []
        self.tagged_containers = {}
        self.parent = None
        self.grid_size = None
        self.absolute_location = None
        self.absolute_size = None
        self._finalized = False

    def set_dimensions(self, value):
        """
        Will change the dimensions of this container.
        It's assumed that this is an empty leaf container because
        why would you add a container to something and then change
        the layout of it.
        :param value:
        :return:
        """
        self.dimensions = value
        self.finalize(
            self.absolute_size,
            pixel_location=self.absolute_location,
            depth=self.depth
        )

    def create(self, location=None, size=None, tag=None, dimensions=None):
        """
        Creates a container as a child of the current child.

        By default, will clone the current container and make that as a child.
        :param location:
        :param size:
        :param tag:
        :param dimensions:
        :return:
        """
        location = location if location else (0, 0)
        size = size if size else self.dimensions
        dimensions = dimensions if dimensions else self.dimensions
        child = Container(location, size, tag=tag, dimensions=dimensions)
        self.add(child)
        return child

    def calculate_location(self, child):
        return (
            int((self.grid_size[0] * child.location[0]) + self.absolute_location[0]),
            int((self.grid_size[1] * child.location[1]) + self.absolute_location[1])
        )

    def calculate_size(self, child):
        return (
            int(self.grid_size[0] * child.size[0]),
            int(self.grid_size[1] * child.size[1])
        )

    def add(self, child):
        """
        Adds a pre-made container as a child of the current container.
        :param child:
        :return:
        """
        self.children.append(child)
        child.parent = self

        # process tags
        # first, collect all fo the tags of the child including its own.
        tags_to_process = dict((key, child.tagged_containers[key]) for key in child.tagged_containers.keys())
        if child.tag is not None:
            tags_to_process[child.tag] = child

        # now go up the chain, adding tags to each tagged containers collection.
        curr_parent = self
        while curr_parent:
            for tag in tags_to_process.keys():
                if tag in curr_parent.tagged_containers:
                    raise LayoutException("Duplicate container tag %s found." % tag)
                curr_parent.tagged_containers[tag] = tags_to_process[tag]
            curr_parent = curr_parent.parent
        if self._finalized:
            child.finalize(
                (self.calculate_size(child)),
                (self.calculate_location(child)),
                depth=self.depth+1
            )
        return child

    def container(self, tag=None, location=None):
        """
        Fetches a container with the provided tag, at the specified
        row and column location (by creating an anonymous container).
        :param tag:
        :return:
        """
        if tag:
            if tag not in self.tagged_containers:
                raise LayoutException("Tagged container %s does not exist" % tag)
            return self.tagged_containers[tag]
        if location:
            for index in [0, 1]:
                if location[index] < 0 or location[index] >= self.dimensions[index]:
                    raise LayoutException("Requested location %s outside of bounds of container %s." % (str(location), str(self.dimensions)))
                size = (1, 1)
                to_return = Container(location, size)
                to_return.finalize(
                    (self.calculate_size(to_return)),
                    (self.calculate_location(to_return)),
                    depth=self.depth+1
                )
                return to_return

    def finalize(self, pixel_dimensions, pixel_location=(0, 0), depth=0):
        """
        Finalize does some basic validation checks on the layout,
        then will calculate the actual pixel values of dimensions and locations
        of itself and call finalize on all children.
        :param pixel_dimensions:
        :param pixel_location:
        :param depth:
        :return:
        """
        self.validate()
        self.absolute_location = pixel_location
        self.absolute_size = pixel_dimensions
        self.depth = depth
        self.grid_size = (pixel_dimensions[0] / self.dimensions[0], pixel_dimensions[1] / self.dimensions[1])
        self._finalized = True

        for child in self.children:
            child.finalize(
                (self.calculate_size(child)),
                (self.calculate_location(child)),
                depth=depth+1
            )

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
    def convert(cls, xml_data, parser):
        """
        Used primarily in converting a layout XML file into a series
        of Container objects.
        :param xml_data:
        :param parser:
        :return:
        """
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
                    new_layout.add(Container.convert(element, parser))
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




