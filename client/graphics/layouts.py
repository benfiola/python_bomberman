from lxml import etree
import xmltodict
from io import StringIO

class GridElement(object):
    def __init__(self, grid_loc, grid_size):
        self.grid_location = grid_loc
        self.grid_size = grid_size
        self.layout = None

    def create_layout(self, grid_dimensions):
        self.layout = GridLayout(grid_dimensions)
        return self.layout


class GridLayout(object):
    def __init__(self, grid_dimensions):
        self.grid_dimensions = grid_dimensions
        self.children = {}

        # these are figured out once we know the screen dimensions
        self.cell_size = None
        self.dimensions = None
        self.top_left = None

    def add_child(self, entity, location, dimensions):
        elem = GridElement(location, dimensions)
        self.children[entity] = elem
        return elem

    def finalize(self, dimensions):
        self._finalize_helper((0, 0), dimensions)
        return self.sprite_dimension_data()

    def _finalize_helper(self, top_left, dimensions):
        self.top_left = top_left
        self.dimensions = dimensions
        self.cell_size = (self.dimensions[0] / self.grid_dimensions[0], self.dimensions[1] / self.grid_dimensions[1])
        for obj in self.children.values():
            if obj.layout:
                top_left = (self.top_left[0] + (self.cell_size[0] * obj.grid_location[0]), self.top_left[1] + (self.cell_size[1] * obj.grid_location[1]))
                dimensions = (self.cell_size[0] * obj.grid_size[0], self.cell_size[1] * obj.grid_size[1])
                obj.layout._finalize_helper(top_left, dimensions)

    def sprite_dimension_data(self):
        to_return = {}
        self._sprite_dimension_data(to_return)
        return to_return

    def _sprite_dimension_data(self, to_return):
        for element in self.children.keys():
            obj = self.children[element]
            top_left = (int(self.top_left[0] + (self.cell_size[0] * obj.grid_location[0])), int(self.top_left[1] + (self.cell_size[1] * obj.grid_location[1])))
            dimensions = (int(self.cell_size[0] * obj.grid_size[0]), int(self.cell_size[1] * obj.grid_size[1]))
            to_return[element] = (top_left, dimensions)
            if obj.layout:
                obj.layout._sprite_dimension_data(to_return)


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
        print(xml_dict)

LayoutParser.generate_layout('layout.xml')




