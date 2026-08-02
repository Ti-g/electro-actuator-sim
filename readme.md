# Overview

![MIT License](https://img.shields.io/badge/License-MIT-F3F4F4?style=flat-square&logoColor=black)
![EM](https://img.shields.io/badge/Physics-Electromagnetics-0DFDF7?style=flat-square&logo=physics&)

A `voice-coil` actuator is an electromechanical device that produces linear motion using an inner permanent magnet (dipole) on a shaft and an outer coil to produce force via `magnetic co-energy interaction` between the field sources.

<div align="center">
  <img src="01_media/reference_design.png" alt="Reference topology" style="max-width:600px;">
  <p><em>Figure 1: Quarter-sectional view of the voice-coil actuator topology showing the permanent magnet (dipole) and coil arrangement.</em></p>
</div>

> [!note]
> Editor Note: The model seems reasonable enough for now. It should be validated if it's used for actual actuator design. I encourage anyone else to do the same.

## Mathematical Implementation

The model is constructed using axisymmetric coordinates due to the axial symmetry of a voice coil. The model also assumes the domain has a relative permeability of $\mu_r = 1$.
This assumption allows the model to use a simplified superposition model to calculate the co-energy and then virtual work. The specific model for virtual work is shown here:

$$ U = A_{\text{rad}} \cdot \mu_0 \cdot \int_{\Omega} \left( H_{\text{pole}}(z-z_{t}) \cdot H_{\text{coil}}(z) \right) \, dz $$

$$ F = -\frac{dU}{dz} \approx -\frac{U(z+\Delta z) - U(z-\Delta z)}{2\Delta z}$$

The field strength formulas for the magnet (dipole) and coil are:

$$
H_{\text{dipole}}(z, m) = h_{\text{peak}} \left[ \mathrm{sech}\left( \frac{n\left((z-m) +\ell_{\text{dipole}}/2 \right)}{\ell_{\text{dipole}}} \right)^2 -\mathrm{sech}\left(\frac{n\left((z-m) -\ell_{\text{dipole}}/2 \right)}{\ell_{\text{dipole}}} \right)^2 \right]
$$

The parameter `n` determines the decay rate of the pole field along the z-axis and `m` is the translation over the z-axis. The coil formula is more complex, as it involves modelling two different poles, each containing half the total number of turns, and then superimposing their fields.

$$
H_{\text{pole}}(z) = \frac{N I}{4\pi} \int_{-\ell_{\text{pole}}/2}^{\ell_{\text{pole}}/2} 
\frac{R^2}{\left[(z - z')^2 + R^2\right]^{3/2}} \, dz'
$$

$$ H_{\text{coil}}(z) = H_{\text{pole}}(z + \ell_{\text{coil}}/2) - H_{\text{pole}}(z - \ell_{\text{coil}}/2) $$

> [!important]
> The parameter `N` is the turn density of the pole (`turns/length`).

## Computational Implementation

The model was constructed using `picounits` and implements the virtual work method using the limit of the field in $(-z, z)$:

$$ U = A_{\text{rad}} \cdot \mu_0 \cdot \lim_{N \to \infty} \sum_{i=1}^{N} \left( H_{\text{dipole}}(z-z_{t}) \cdot H_{\text{coil}}(z) \right) \, dz $$

$$ \Omega = \{ z \mid |H_{\text{dipole}}(z)| > \varepsilon \quad \text{or} \quad |H_{\text{coil}}(z)| > \varepsilon \}$$

$A_{\text{rad}}$ is the effective area through which the magnetic field passes. The force is then calculated using the finite difference approach:

$$ F = -\frac{dU}{dz} \approx -\frac{U(z+\Delta z) - U(z-\Delta z)}{2\Delta z}$$

## Installation

> [!IMPORTANT]
> Do not assume the resulting design variables are suitable for fabrication or real-world use without further analysis.

<div align="center">
  <img src="01_media/force_vs_position.png" alt="Force vs position example" style="max-width:600px;">
  <p><em>Figure 2: Simulated force vs. position for a single voice-coil actuator.</em></p>
</div>

> [!note]
> Model: [00_simulation/](00_simulation/main.py)  
> Parameters: [parameters.uiv](00_simulation/parameters.uiv)

To run the analytical model, the following packages are required:

```bash
pip install picounits matplotlib
```