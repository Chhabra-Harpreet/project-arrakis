import unittest
import numpy as np


class TestObliqueShockResponse(unittest.TestCase):
    def test_oblique_shock(self):
        from src.test_cases.oblique_shock_data import ObliqueShock
        os = ObliqueShock()
        os.mach = 2.3
        os.deflection = 10
        os.compute()
        self.assertAlmostEqual(os.shock_angle.all(), np.array([34.32642717, 85.02615188]).all(), places=4)

    def test_oblique_shock_relation(self):
        from src.test_cases.oblique_shock_data import ObliqueShock
        from src.test_cases.oblique_shock_data import ObliqueShockData
        os = ObliqueShock()
        os.mach = 2.3
        os.deflection = 10
        os.compute()

        # Create grid and flow files
        osd = ObliqueShockData()
        osd.nx_max = 10
        osd.ny_max = 10
        osd.nz_max = 10
        osd.inlet_density = 1.273
        osd.inlet_temperature = 300
        osd.inlet_pressure = 101325
        osd.points = 100
        osd.oblique_shock = os
        osd.create_grid()
        osd.create_flow()


if __name__ == '__main__':
    unittest.main()
