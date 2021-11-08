# This file contains classes for plot3d data io
# TODO: implement output for p3d data - Assigned to Harpreet.
#  Each output function should be added to respective GridIO/FlowIO classes
#  Change docstrings for doctest in test_io

import numpy as np


class GridIO:
    """Module to read-in a grid file and output grid parameters

    ...

    Attributes
    ----------
    Input :
        filename : str
            name of the grid file
    Output :
        nb : int
            number of blocks in the grid
        ni, nj, nk : int
            shape of the domain
        grd : numpy.ndarray
            Grid data of shape (ni, nj, nk, 3, nb)

    Methods
    -------
    read_grid()
        returns the output attributes

    Example:
        grid = GridIO('plate.sp.x')  # Assume file is in the path
        grid.read_grid()  # Call method to read the data
        print(grid)  # prints the docstring for grid
        # Instance attributes
        print(grid.grd.shape)  # shape of the grid data
        print(grid.nb)  # Number of blocks

    author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
    date: 10-05/2021
    """

    def __init__(self, filename):
        self.filename = filename
        self.nb = None
        self.ni, self.nj, self.nk = None, None, None
        self.grd = None

    def __str__(self):
        doc = "This instance has the filename " + self.filename + "\n" + \
              "grd attribute is of shape (ni, nj, nk, 3, nb), rows representing x,y,z coordinates for each block\n" \
              "For example, x = grid.grd(...,0, 0), grid being the object.\n" \
              "Use method 'read_grid' to compute attributes:\n" \
              "ni, nj, nk, ng\n" \
              "grd -- The grid data\n"
        return doc

    def read_grid(self, data_type='f4'):
        """Reads in the grid file and changes the instance attributes

        :parameter

        :return
        None

        author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
        credit: Paul Orkwis
        date: 11-04/2021
        """
        with open(self.filename, 'r') as grid:
            # Read-in number of blocks
            self.nb = np.fromfile(grid, dtype='i4', count=1)[0]

            # Read-in i, j, k for all blocks
            _temp = np.fromfile(grid, dtype='i4', count=3 * self.nb)
            self.ni, self.nj, self.nk = _temp[0::3], _temp[1::3], _temp[2::3]

            # length of grd data
            _nt = self.ni * self.nj * self.nk * 3
            # read the grd data from file to temp_array
            _temp = np.fromfile(grid, dtype=data_type, count=sum(_nt))

            # pre-define grd to reduce calling pad and concatenate
            self.grd = np.zeros((self.ni.max(), self.nj.max(), self.nk.max(), 3, self.nb))

            # Reshape and assign data to grd
            for _i in range(self.nb):
                self.grd[0:self.ni[_i], 0:self.nj[_i], 0:self.nk[_i], 0:3, _i] = \
                    _temp[sum(_nt[0:_i]):sum(_nt[0:_i]) + _nt[_i]] \
                    .reshape((self.ni[_i], self.nj[_i], self.nk[_i], 3), order='F')

            print("Grid data reading is successful for " + self.filename + "\n")


class FlowIO:
    """Module to read-in a flow file and output flow parameters

    ...

    Attributes
    ----------
    Input :
        filename : str
            name of the flow file
    Output :
        nb : int
            number of blocks in the grid
        ni, nj, nk : int
            shape of the domain
        mach, alpha, rey, time: float
            extra numerics needed for post-processing
        q : numpy.ndarray
            Flow data of shape (ni, nj, nk, 5, nb)

    Methods
    -------
    read_flow()
        returns the output attributes

    Example:
        grid = FlowIO('plate.sp.x')  # Assume file is in the path\n
        flow.read_flow()  # Call method to read the data\n
        print(flow)  # prints the docstring for grid\n
        # Instance attributes\n
        print(flow.q.shape)  # shape of the flow data\n
        print(flow.ng)  # Number of blocks


    author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
    date: 10-05/2021
    """

    def __init__(self, filename):
        self.filename = filename
        self.nb = None
        self.ni, self.nj, self.nk = None, None, None
        self.mach = None
        self.alpha = None
        self.rey = None
        self.time = None
        self.q = []

    def __str__(self):
        doc = "This instance has the filename " + self.filename + "\n" + \
              "q attribute is of shape (ni, nj, nk, 5, nb), rows representing density, momentum[*3], energy" \
              "for every block\n" \
              "For example, rho = flow.q(...,0,0), flow being the object for block-1.\n" \
              "Use method 'read_flow' to compute attributes:\n" \
              "nb, ni, nj, nk\n" \
              "mach, alpha, rey, time\n" \
              "q -- The flow data\n"
        return doc

    def read_flow(self, data_type='f4'):
        """Reads in the flow file and changes the instance attributes

        Parameters
        ----------

        Returns
        -------
        None

        author: Dilip Kalagotla @ kal ~ dilip.kalagotla@gmail.com
        credit: Paul Orkwis
        date: 10-05/2021
        """
        with open(self.filename, 'r') as data:
            self.nb = np.fromfile(data, dtype='i4', count=1)[0]

            # Read in the i, j, k values for blocks
            _temp = np.fromfile(data, dtype='i4', count=3 * self.nb)
            self.ni, self.nj, self.nk = _temp[0::3], _temp[1::3], _temp[2::3]

            # Read-in flow data into a temp array
            # Less use of fromfile is more speed
            _nt = self.ni * self.nj * self.nk * 5
            _temp = np.fromfile(data, dtype=data_type, count=sum(_nt) + 4 * self.nb)

            # Create a mask to remove dimensionless quantities from q
            # Indices of the first four dimensionless quantities
            _index_array = np.array([0, 1, 2, 3])
            for i in range(len(_nt) - 1):
                _term = sum(_temp[0:i]) + (i + 1) * 4
                _index_array = np.concatenate((_index_array, np.arange(_term, _term + 4)))
            _mask = np.ones(len(_temp), dtype='bool')
            _mask[_index_array] = 0
            # Use the mask to remove dimensionless quantities
            _temp = _temp[_mask]

            # Assign the dimensionless attributes
            self.mach, self.alpha, self.rey, self.time = _temp[0:4]

            # Pre-define q array
            self.q = np.zeros((self.ni.max(), self.nj.max(), self.nk.max(), 5, self.nb))

            # Reshape and assign data to q
            for _i in range(1, self.nb):
                self.q[self.ni[_i], self.nj[_i], self.nk[_i], 5, _i] = \
                    _temp[sum(_nt[0:_i]):sum(_nt[0:_i]) + _nt[_i]] \
                    .reshape((self.ni[_i], self.nj[_i], self.nk[_i], 5), order='F')

            print("Flow data reading is successful for " + self.filename + "\n")
