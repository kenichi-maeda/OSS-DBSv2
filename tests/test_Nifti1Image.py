
from src.brain_imaging.Nifti1Image import Nifti1Image
import numpy as np
import pytest
import nibabel


class TestNifti1Image:
    @pytest.fixture
    def nifti1_image_3d(self, tmpdir):
        path = tmpdir.mkdir("Test_Nifti1Image").join("test_Nifti1Image_3d.nii")
        data = np.array([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]])
        affine = np.array([[0.5, 0, 0, 2],
                           [0, 0.5, 0, 2],
                           [0, 0, 0.5, 2],
                           [0, 0, 0, 1]])
        nii_image = nibabel.Nifti1Image(dataobj=data, affine=affine)
        nibabel.save(nii_image, path)
        return Nifti1Image(file_path=path)

    @pytest.fixture
    def nifti1_image_4d(self, tmpdir):
        path = tmpdir.mkdir("Test_Nifti1Image").join("test_Nifti1Image_4d.nii")
        data = np.array([[[[1.0], [2.0]], [[3.0], [4.0]]],
                        [[[5.0], [6.0]], [[7.0], [8.0]]]])
        affine = np.array([[0.5, 0, 0, 2],
                           [0, 0.5, 0, 2],
                           [0, 0, 0.5, 2],
                           [0, 0, 0, 1]])
        nii_image = nibabel.Nifti1Image(dataobj=data, affine=affine)
        nibabel.save(nii_image, path)
        return Nifti1Image(file_path=path)

    def test_inavlid_file_path(self):
        with pytest.raises(IOError):
            Nifti1Image(file_path='inavlid_file_path')

    def test_data_file(self, nifti1_image_3d):
        desired = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])
        np.testing.assert_equal(nifti1_image_3d.data_map(), desired)

    def test_boundingbox_units_default(self, nifti1_image_3d):
        desired = (2, 2, 2), (3, 3, 3)
        np.testing.assert_equal(nifti1_image_3d.bounding_box(), desired)

    def test_boundingbox_4d_shape(self, nifti1_image_4d):
        desired = (2, 2, 2), (3, 3, 3)
        np.testing.assert_equal(nifti1_image_4d.bounding_box(), desired)

    def test_boundingbox_units_mm(self, nifti1_image_3d):
        nifti1_image_3d.header()['xyzt_units'] = 2
        desired = (2, 2, 2), (3, 3, 3)
        np.testing.assert_equal(nifti1_image_3d.bounding_box(), desired)

    def test_boundingbox_units_meter(self, nifti1_image_3d):
        nifti1_image_3d.header()['xyzt_units'] = 1
        desired = (2000, 2000, 2000), (3000, 3000, 3000)
        np.testing.assert_equal(nifti1_image_3d.bounding_box(), desired)

    def test_boundingbox_units_micron(self, nifti1_image_3d):
        nifti1_image_3d.header()['xyzt_units'] = 3
        desired = (0.002, 0.002, 0.002), (0.003, 0.003, 0.003)
        np.testing.assert_equal(nifti1_image_3d.bounding_box(), desired)

    def test_bounding_box_shift(self, nifti1_image_3d):
        nifti1_image_3d.set_offset((1, 2, 3))
        desired = (3, 4, 5), (4, 5, 6)
        np.testing.assert_equal(nifti1_image_3d.bounding_box(), desired)

    def test_voxel_size(self, nifti1_image_3d):
        desired = (0.5, 0.5, 0.5)
        np.testing.assert_equal(nifti1_image_3d.voxel_size(), desired)
