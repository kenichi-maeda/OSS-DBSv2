# Boston Scientific (Marlborough, Massachusetts, USA) vercise
from src.electrodes.abstract_electrode import AbstractElectrode
import netgen
import numpy as np


class BostonScientificVercise(AbstractElectrode):
    """Boston Scientific (Marlborough, Massachusetts, USA) vercise electrode.

    Attributes
    ----------
    rotation : float
        Rotation angle in degree of electrode.

    direction : tuple
        Direction vector (x,y,z) of electrode.

    translation : tuple
        Translation vector (x,y,z) of electrode.

    Methods
    -------
    generate_geometry()
        Generate geometry of electrode.
    """
    # dimensions [mm]
    TIP_LENGTH = 1.1
    CONTACT_LENGTH = 1.5
    CONTACT_SPACING = 0.5
    LEAD_DIAMETER = 1.3
    TOTAL_LENGHTH = 50.0
    CONTACT_SPACING_RADIAL = 0.25

    def __init__(self,
                 rotation: float = 0.0,
                 direction: tuple = (0, 0, 1),
                 translation: tuple = (0, 0, 0)) -> None:
        self.__translation = translation
        norm = np.linalg.norm(direction)
        self.__direction = tuple(direction / norm) if norm else (0, 0, 1)

    def generate_geometry(self) -> netgen.libngpy._meshing.Mesh:
        """Generate geometry of electrode.

        Returns
        -------
        geometry : netgen.libngpy._NgOCC.TopoDS_Shape
        """
        contacts = self.__contacts()
        body = self.__body() - contacts
        electrode = netgen.occ.Glue([body, contacts])
        axis = netgen.occ.Axis(p=(0, 0, 0), d=self.__direction)
        rotated_electrode = electrode.Rotate(axis=axis, ang=self.__rotation)
        return rotated_electrode.Move(self.__translation)

    def __body(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        center = tuple(np.array(self.__direction) * self.LEAD_DIAMETER * 0.5)
        body = netgen.occ.Cylinder(p=center,
                                   d=self.__direction,
                                   r=self.LEAD_DIAMETER * 0.5,
                                   h=self.TOTAL_LENGHTH - self.TIP_LENGTH)
        body.bc("Body")
        return body

    def __contacts(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        axis = netgen.occ.Axis((0, 0, 0), self.__direction)

        distance_1 = self.TIP_LENGTH + self.CONTACT_SPACING
        distance_2 = distance_1 + self.CONTACT_LENGTH + self.CONTACT_SPACING
        distance_3 = distance_2 + self.CONTACT_LENGTH + self.CONTACT_SPACING

        vector_1 = tuple(np.array(self.__direction) * distance_1)
        vector_2 = tuple(np.array(self.__direction) * distance_2)
        vector_3 = tuple(np.array(self.__direction) * distance_3)

        contact = netgen.occ.Cylinder(p=(0, 0, 0),
                                      d=self.__direction,
                                      r=self.LEAD_DIAMETER * 0.5,
                                      h=self.CONTACT_LENGTH)

        contact_directed = self.__contact_directed()

        contacts = [self.__active_tip(),
                    contact_directed.Move(vector_1),
                    contact_directed.Rotate(axis, 120).Move(vector_1),
                    contact_directed.Rotate(axis, 240).Move(vector_1),
                    contact_directed.Move(vector_2),
                    contact_directed.Rotate(axis, 120).Move(vector_2),
                    contact_directed.Rotate(axis, 240).Move(vector_2),
                    contact.Move(vector_3)
                    ]

        for index, contact in enumerate(contacts, 1):
            contact.bc("Contact_{}".format(index))

        return netgen.occ.Fuse(contacts)

    def __active_tip(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        radius = self.LEAD_DIAMETER * 0.5
        point = tuple(np.array(self.__direction) * self.TIP_LENGTH)
        space = netgen.occ.HalfSpace(p=point, n=self.__direction)
        center = tuple(np.array(self.__direction) * radius)
        active_tip_pt1 = netgen.occ.Sphere(c=center, r=radius) * space
        active_tip_pt2 = netgen.occ.Cylinder(p=center,
                                             d=self.__direction,
                                             r=radius,
                                             h=self.TIP_LENGTH - radius)
        active_tip = netgen.occ.Fuse([active_tip_pt1, active_tip_pt2])
        return active_tip

    def __contact_directed(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        body = netgen.occ.Cylinder(p=(0, 0, 0),
                                   d=self.__direction,
                                   r=self.LEAD_DIAMETER * 0.5,
                                   h=self.CONTACT_LENGTH)
        new_direction = tuple(np.cross(self.__direction_2(), self.__direction))
        eraser = netgen.occ.HalfSpace(p=(0, 0, 0), n=new_direction)
        delta = self.CONTACT_SPACING_RADIAL / self.LEAD_DIAMETER * 180 / np.pi
        angle = 30 + delta
        axis = netgen.occ.Axis((0, 0, 0), self.__direction)
        return body - eraser.Rotate(axis, angle) - eraser.Rotate(axis, -angle)

    def __direction_2(self):
        x, y, z = self.__direction

        if not x and not y:
            return (0, 1, 0)

        if not x and not z:
            return (0, 0, 1)

        if not y and not z:
            return (0, 1, 0)

        return (x, y, not z)
