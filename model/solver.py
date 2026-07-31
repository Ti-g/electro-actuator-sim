"""
Filename: solver.py

Description:
    Solver class designed for solving voice coil
    problem using virtual work methods
"""

from builtins import float as f
from math import pi

from picounits import DynamicLoader, strip_quantity as validate
from picounits import length, voltage, conductivity, coercivity, nullset

from model import equations


class Solver:
    """
    Magnetic Solver for voice coil problem.
    COmputes electromagnetic force using magnetic energy and virtual work methods.
    """
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the solver class """
        self._extract_validate(parameters)
        self.permeability = 4 * pi * 10 ** -7
        self.current = 0.0

        # Computes derived values from parameters
        self._compute_derived_values()

    def compute_force(self, z_pos: f, polarity: bool = True) -> f:
        """ Computes force using finite difference of the energy distribution """
        # Calculates the energy one step forward and one backward
        self.current = abs(self.current) if polarity else -abs(self.current)

        pos = self._compute_energy_state(z_pos + self.int_step_size, self.int_step_size)
        neg = self._compute_energy_state(z_pos - self.int_step_size, self.int_step_size)

        return - 4 * (pos - neg) / (2 * self.int_step_size)

    def _compute_energy_state(
        self, translate: f, dz: f, epsilon: float = 1e-8, window: int = 5
    ) -> f:
        """ Computes the co-energy interaction over the relevant domain. """
        positive = self._integrate_sample(dz, translate, epsilon, window)
        negative = self._integrate_sample(-dz, translate, epsilon, window)

        # Integrate cached values
        sum_energy = sum(positive) + sum(negative)
        energy = self.effective_area * self.permeability * sum_energy * dz
        return energy

    def _integrate_sample(self, dz: f, translate: f, epsilon: f, window: int) -> list[f]:
        """ Integrates the co-energy interaction in one direction """
        interactions = []
        z = 0.0
        below_epsilon = 0

        while True:
            # Computes the coil field strength at z
            h_coil = equations.compute_coil_z_field_strength(
                z, translate,
                self.current,
                self.stage_turns,
                self.coil_axial_length,
                self.coil_mean_radius
            )

            # Computes the magnet field strength at z
            h_magnet = equations.compute_pole_z_field_strength(
                z,
                0,
                self.pole_axial_length, 
                self.coercivity
            )

            # Computes the co-energy from that interaction
            interaction = h_coil * h_magnet
            interactions.append(interaction)

            if abs(interaction) <= epsilon:
                below_epsilon += 1
            else:
                below_epsilon = 0

            # Breaks loop if below epsilon for more than window iterations
            if below_epsilon >= window: 
                break

            # Moves along the z-axis
            z += dz

        return interactions

    def _compute_derived_values(self) -> None:
        """ Computes derived values based on parameters """
        self.coil_inner_radius = self.pole_radial_thickness + self.radial_clearance
        self.coil_mean_radius = self.coil_inner_radius + self.coil_radial_thickness / 2
        self.effective_area = pi * self.coil_mean_radius ** 2

        # Computes the number of turns and inductance
        self.stage_turns = equations.compute_turns(
            self.coil_axial_length, 
            self.coil_radial_thickness, 
            self.wire_diameter,
            self.fill_factor
        )

        self.stage_inductance = equations.compute_inductance(
            self.stage_turns,
            self.coil_axial_length,
            self.coil_mean_radius,
            self.permeability
        )

        # Computes the resistivity and resistance of a coil
        resistivity = 1 / self.conductivity
        self.stage_resistance = equations.compute_resistance(
            self.stage_turns,
            self.coil_mean_radius,
            self.wire_diameter,
            resistivity
        )

        # Computes the equivalent resistance and inductance
        self.total_resistance = self.stage_resistance / 4
        self.total_inductance = self.stage_inductance / 4

        # Computes the total current carrying capacity
        self.current = self.line_voltage / self.total_resistance

    def _extract_validate(self, parameters: DynamicLoader) -> None:
        """ Extracts qualities from attribute tree and validates units """
        # Numerical
        self.int_step_size = validate(parameters.numerics.integration_step_size, length)
        self.line_voltage = validate(parameters.numerics.line_voltage, voltage)

        # Coil
        self.radial_clearance = validate(parameters.coil.pole_radial_clearance, length)
        self.coil_radial_thickness = validate(parameters.coil.radial_thickness, length)
        self.coil_axial_length = validate(parameters.coil.axial_length, length)
        self.wire_diameter = validate(parameters.coil.wire_diameter, length)
        self.conductivity = validate(parameters.coil.conductivity, conductivity)
        self.fill_factor = validate(parameters.coil.fill_factor, nullset)

        # Pole
        self.coercivity = validate(parameters.pole.coercivity, coercivity)
        self.pole_radial_thickness = validate(parameters.pole.radial_thickness, length)
        self.pole_axial_length = validate(parameters.pole.axial_length, length)
