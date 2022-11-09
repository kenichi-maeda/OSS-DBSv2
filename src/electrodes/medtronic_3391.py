# Medtronic 3391
from src.electrodes.abstract_electrode import AbstractElectrode
import netgen
import numpy as np


class Medtronic3391(AbstractElectrode):
    """Medtronic 3389 electrode.

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
    TIP_LENGTH = 1.5
    CONTACT_LENGTH = 3.0
    CONTACT_SPACING = 3.5
    LEAD_DIAMETER = 1.27
    TOTAL_LENGHTH = 100.0
    N_CONTACTS = 4

    def __init__(self,
                 rotation: float = 0.0,
                 direction: tuple = (0, 0, 1),
                 translation: tuple = (0, 0, 0)) -> None:
        self.__translation = translation
        norm = np.linalg.norm(direction)
        self.__direction = tuple(direction / norm) if norm else (0, 0, 1)

    def generate_geometry(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        """Generate geometry of electrode.

        Returns
        -------
        geometry : netgen.libngpy._NgOCC.TopoDS_Shape
        """
        contacts = self.__contacts()
        body = self.__body() - contacts
        electrode = netgen.occ.Glue([body, contacts])
        return electrode.Move(self.__translation)

    def __body(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        radius = self.LEAD_DIAMETER * 0.5
        center = tuple(np.array(self.__direction) * radius)
        tip = netgen.occ.Sphere(c=center, r=radius)
        lead = netgen.occ.Cylinder(p=center,
                                   d=self.__direction,
                                   r=radius,
                                   h=self.TOTAL_LENGHTH - self.TIP_LENGTH)
        body = tip + lead
        body.bc("Body")
        return body

    def __contacts(self) -> netgen.libngpy._NgOCC.TopoDS_Shape:
        contact = netgen.occ.Cylinder(p=(0, 0, 0),
                                      d=self.__direction,
                                      r=self.LEAD_DIAMETER * 0.5,
                                      h=self.CONTACT_LENGTH)

        length = (self.CONTACT_LENGTH + self.CONTACT_SPACING)
        distrances = np.arange(self.N_CONTACTS) * length + self.TIP_LENGTH
        contacts = [contact.Move(tuple(np.array(self.__direction) * distance))
                    for distance in distrances]

        for index, contact in enumerate(contacts, 1):
            contact.bc("Contact_{}".format(index))

        return netgen.occ.Glue(contacts)
