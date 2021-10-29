# Use tri-linear interpolation to get data at the given point

import numpy as np


class Interpolation:
    """
    Module to do the cell data interpolation to the given point

    ...

    Attributes
    ----------
    Input:
        grid : src.io.plot3dio.GridIO
            Grid object created from GridIO
        flow : src.io.plot3dio.FlowIO
            Flow object created from FlowIO
        idx: src.streamlines.Search
            Index object created from Search
    Output:
        q : ndarray
            Interpolated data at the given point

    Methods
    -------
    compute(method='linear')
        Interpolates the data onto a given point

    Example:
        grid = GridIO('../data/plate_data/plate.sp.x')
        flow = FlowIO('../data/plate_data/sol-0000010.q')
        idx = Search(grid, [8.5, 0.5, 0.01])
        interp_data = Interpolation(grid, flow, idx)

        grid.read_grid()
        flow.read_flow()
        idx.compute()
        interp_data.compute()  # method='linear' is default

    author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
    date: 10-29/2021
    """

    def __init__(self, grid, flow, idx):
        self.grid = grid
        self.flow = flow
        self.idx = idx
        self.q = None

    def compute(self, method='linear'):

        # If out of domain return
        if self.idx.info == 'Given point is not in the domain. The cell attribute will return "None"\n':
            print('Cannot run interpolation. The given point is out of domain.\n')
            self.q = None
            return

        # Obtain grid data from nodes found from the search method
        _cell_grd = np.zeros(self.idx.cell.shape)
        _cell_grd = self.grid.grd[self.idx.cell[:, 0], self.idx.cell[:, 1], self.idx.cell[:, 2], :]

        # Obtain flow data from nodes found
        _cell_q = np.zeros((self.idx.cell.shape[0], 5))
        _cell_q = self.flow.q[self.idx.cell[:, 0], self.idx.cell[:, 1], self.idx.cell[:, 2], :]

        # "Tri"Linear interpolation
        if method == 'linear':
            # If the node is found in a cell
            if self.idx.cell.shape == (8, 3) and self.idx.info is None:
                def _f(_m, _n, _arr1, _arr2, _axis, _paxis, _data1, _data2):
                    """
                    Internal function used for linearly interpolating data
                    :param _m: int
                        point-1 for interpolation
                    :param _n: int
                        point-2 for interpolation
                    :param _arr1: ndarray
                        data with point-1
                    :param _arr2: ndarray
                        data with point-2
                    :param _axis: int
                        assign x, y or z axis to consider for interpolation
                    :param _paxis: int
                        assign point's x, y, or z for interpolation
                    :param _data1: ndarray/list
                        data at point-1 to be interpolated. List is provided when moving across axis
                    :param _data2: ndarray/list
                        data at point-2 to be interpolated. List is provided when moving across axis
                    :return: None

                    author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
                    date: 10-29/2021
                    """
                    _a = (_arr2[_n, _axis] - self.idx.point[_paxis]) / (_arr2[_n, _axis] - _arr1[_m, _axis]) * _data1[_m]
                    _b = (self.idx.point[_paxis] - _arr1[_m, _axis]) / (_arr2[_n, _axis] - _arr1[_m, _axis]) * _data2[_n]
                    return _a + _b

                # 0123 are vertices of quadrilateral
                # Doing interpolation to x location in self.idx.point
                # Values in the function help set the linear interpolation in x-direction
                _cell_grd_01 = _f(0, 1, _cell_grd, _cell_grd, 0, 0, _cell_grd, _cell_grd)
                _cell_grd_32 = _f(3, 2, _cell_grd, _cell_grd, 0, 0, _cell_grd, _cell_grd)
                _cell_q_01 = _f(0, 1, _cell_grd, _cell_grd, 0, 0, _cell_q, _cell_q)
                _cell_q_32 = _f(3, 2, _cell_grd, _cell_grd, 0, 0, _cell_q, _cell_q)

                # Doing interpolation to the point projection on the face
                _cell_grd_0123 = _f(1, 1, _cell_grd_01, _cell_grd_32, None, 1, [None, _cell_grd_01], [None, _cell_grd_32])
                _cell_q_0123 = _f(1, 1, _cell_grd_01, _cell_grd_32, None, 1, [None, _cell_q_01], [None, _cell_q_32])

                # 4567 face
                # Doing interpolation to x location in self.idx.point
                # Values in the function help set the linear interpolation in y-direction
                _cell_grd_45 = _f(4, 5, _cell_grd, _cell_grd, 0, 0, _cell_grd, _cell_grd)
                _cell_grd_76 = _f(7, 6, _cell_grd, _cell_grd, 0, 0, _cell_grd, _cell_grd)
                _cell_q_45 = _f(4, 5, _cell_grd, _cell_grd, 0, 0, _cell_q, _cell_q)
                _cell_q_76 = _f(7, 6, _cell_grd, _cell_grd, 0, 0, _cell_q, _cell_q)

                # Doing interpolation to the point projection on the face
                _cell_grd_4567 = _f(1, 1, _cell_grd_45, _cell_grd_76, None, 1, [None, _cell_grd_45], [None, _cell_grd_76])
                _cell_q_4567 = _f(1, 1, _cell_grd_45, _cell_grd_76, None, 1, [None, _cell_q_45], [None, _cell_q_76])

                # Doing data interpolation to the given point based on the face points
                self.q = _f(2, 2, _cell_grd_0123, _cell_grd_4567, None, 2,
                            [None, None, _cell_q_0123], [None, None, _cell_q_4567])

            # if the point is node return node data
            if self.idx.info == 'Given point is a node in the domain with a tol of 1e-6.\n' \
                                'Interpolation will assign node properties for integration.\n'\
                                'Index of the node will be returned by cell attribute\n':
                self.q = _cell_q