class MaskedArea:
    """Defines masked areas for a masked image item"""

    def __init__(self, geometry=None, x0=None, y0=None, x1=None, y1=None, inside=None):
        self.geometry = geometry
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.inside = inside

    def __eq__(self, other):
        return (
            self.geometry == other.geometry
            and self.x0 == other.x0
            and self.y0 == other.y0
            and self.x1 == other.x1
            and self.y1 == other.y1
            and self.inside == other.inside
        )

    def serialize(self, writer):
        """Serialize object to HDF5 writer"""
        for name in ("geometry", "inside", "x0", "y0", "x1", "y1"):
            writer.write(getattr(self, name), name)

    def deserialize(self, reader):
        """Deserialize object from HDF5 reader"""
        self.geometry = reader.read("geometry")
        self.inside = reader.read("inside")
        for name in ("x0", "y0", "x1", "y1"):
            setattr(self, name, reader.read(name, func=reader.read_float))
