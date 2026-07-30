"""
Filename: equations.py

Description:
    Equations for modelling the
    voice coil actuator
"""

from builtins import float as f
from math import pi, cosh, floor


def compute_coil_z_field_strength(
    z_pos: f, z_start: f, current: f, turns: f, coil_len: f, coil_rad: f
) -> f:
    """
    Computes the field strength at a position z along the coil using the 
    finite continuous solenoid model in axial-symmetric modelling (Z, R).
    
    'z_coil' is in reference to the start of the coil. Hence center is shifted coil_len / 2
    """
    half_length = coil_len / 2
    center = - z_start + half_length

    # Calculates the axial field components (term 1 & term 2)
    denom1 = ((z_pos - center + half_length) ** 2 + coil_rad ** 2) ** 0.5
    term1 = (z_pos - center + half_length) / denom1

    denom2 = ((z_pos - center - half_length) ** 2 + coil_rad ** 2) ** 0.5
    term2 = (z_pos - center - half_length) / denom2

    # Calculates maximal field_strength and returns position dependent strength
    h_term = turns * current / (2 * pi * coil_len)
    return h_term * (term1 - term2)


def compute_pole_z_field_strength(z_pos: f, z_start, pole_len: f, h_field: f, n: int = 4) -> f:
    """ 
    Computes the field strength at a position z along the pole using a sech approximation.
    finite continuous dipole model in axial-symmetric modelling (Z, R).
    
    'z_pole' is in reference to the start of the pole. Hence center is shifted pole_len / 2
    """
    def _sech(x):
        """ Hyperbolic Secant Function """
        try:
            return 1 / cosh(x)
        except OverflowError:
            return 0.0

    half_length = pole_len / 2
    center = z_start + half_length

    # Calculates the axial field components (term 1 & term 2)
    term1 = _sech(n * ((z_pos - center) + half_length) / pole_len) ** 2
    term2 = _sech(n * ((z_pos - center) - half_length) / pole_len) ** 2

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
