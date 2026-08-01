"""
Filename: equations.py

Description:
    Equations for modelling the
    voice coil actuator
"""

from builtins import float as f
from math import pi, cosh, floor


def compute_coil_z_field_strength(
    z_pos: f, current: f, turns: f, length: f, radius: f
) -> f:
    """
    Computes the field strength at a position z along the coil using the 
    finite continuous solenoid model in axial-symmetric modelling (Z, R).
    """
    half_length = length / 2

    # Calculates the axial field components via integration
    term1 = (z_pos + half_length) / (radius ** 2 + (z_pos + half_length) ** 2) ** 0.5
    term2 = (z_pos - half_length) / (radius ** 2 + (z_pos - half_length) ** 2) ** 0.5

    # Calculates maximal field strength and returns position dependent strength
    h_term = turns * current / (2 * length)
    return h_term * (term1 - term2)


def compute_dipole_z_field_strength(z_pos: f, z_start, length: f, h_field: f, n: int = 4) -> f:
    """ 
    Computes the field strength at a position z along the dipole using a sech approximation.
    finite continuous dipole model in axial-symmetric modelling (Z, R).
    """
    def _sech(x):
        """ Hyperbolic Secant Function """
        try:
            return 1 / cosh(x)
        except OverflowError:
            return 0.0

    half_length = length / 2

    # Calculates the axial field components (term 1 & term 2)
    term1 = _sech(n * ((z_pos - z_start) + half_length) / length) ** 2
    term2 = _sech(n * ((z_pos - z_start) - half_length) / length) ** 2

    # Calculates the field strength at `z_pos`
    return h_field * (term1 - term2)


def compute_turns(length: f, thickness: f, wire_diameter: f, fill_factor: f) -> f:
    """ 
    Computes the number of turns while according for the insulation & stacking 
    Assumptions: Fill factor accounts for insulation & stacking
    """
    slot_section = length * thickness
    wire_section = pi * (wire_diameter / 2) ** 2

    effective_area = slot_section * fill_factor
    return floor(effective_area / wire_section)


def compute_inductance(turns: f, coil_len: f, mean_radius: f, permeability: f) -> f:
    """ Calculates the coils self-inductance independent of mutual inductance between coils """
    area = pi * mean_radius ** 2
    return (turns ** 2 * permeability * area) / coil_len


def compute_resistance(turns: f, mean_rad: f, wire_dia: f, resistivity: f) -> f:
    """ 
    Computes the slots resistance by using mean radius & conductor cross section 
    Assumptions: Uses mean radius as an approximate for approximate turn length
    """
    turn_length = 2 * pi * turns * mean_rad
    cross_section = pi * (wire_dia / 2) ** 2

    return resistivity * turn_length / cross_section
