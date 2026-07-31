"""
Filename: main.py

Description:
    Analytical model for voice coil actuator
"""

from pathlib import Path
from math import sqrt
import matplotlib.pyplot as plt

from picounits import Parser
from picounits import current, inductance, resistance, power
from model.solver import Solver

# Loads unit system, material library & parameters
ROOT_DIR = Path(__file__).resolve().parents[0]

# Materials & Parameter files
parameters_path = ROOT_DIR / "parameters.uiv"
parameters = Parser.open(parameters_path, ROOT_DIR / "metric.ut")

# Initialize the solver with parameters
solver = Solver(parameters)
z_sample = parameters.numerics.sampling_size.stripped
z_pos = - z_sample / 2
step = parameters.numerics.integration_step_size.stripped

# Prints out derived parameters for the user
copper_losses = (solver.current / sqrt(2)) ** 2 * solver.total_resistance

print("-" * 10, " Static Parameters ",  "-" * 10)
print(f"Ind: {solver.total_inductance * inductance}, Res: {solver.total_resistance * resistance}")
print(f"Current: {solver.current * current}, Losses: {copper_losses * power}")
print("-" * 10, " Dynamic Parameters ",  "-" * 9)

# Lists to store
z = []
forces_positive = []
forces_negative = []
while z_pos < z_sample / 2:
    # Calculate force with positive polarity
    force_pos = solver.compute_force(z_pos, polarity=True)
    forces_positive.append(force_pos)

    # Calculate force with negative polarity
    force_neg = solver.compute_force(z_pos, polarity=False)
    forces_negative.append(force_neg)

    # Updates z list and the z_pos
    z.append(z_pos)
    z_pos += step


# Create the plot
plt.figure(figsize=(10, 6))

# Plot both polarities
plt.plot(z, forces_positive, 'b-', label='Positive Polarity', linewidth=2)
plt.plot(z, forces_negative, 'r-', label='Negative Polarity', linewidth=2)

plt.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.3)

# Labels and title
plt.xlabel('Z Position (mm)', fontsize=12)
plt.ylabel('Force (N)', fontsize=12)
plt.title('Voice Coil Actuator Force vs Position', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()