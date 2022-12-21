from src.mesh import Mesh
import netgen.occ as occ
import numpy as np
import pytest


class GeometryDummy():
    def __init__(self) -> None:
        model = occ.Box(p1=occ.Pnt(0, 0, 0), p2=occ.Pnt(1, 1, 1))
        model.bc('contact')
        model.mat('saline')
        self.__geometry = occ.OCCGeometry(model)

    def generate_mesh(self):
        return self.__geometry.GenerateMesh()


