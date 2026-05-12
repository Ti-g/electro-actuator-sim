import os
import shutil
from pathlib import Path
import cadquery as cq
import subprocess
import pyelmer as elmer

def main():
    # File paths
    dynamic_object_path = Path("pasiveElement.step")
    config_path = Path("config.conf")
    
    if not dynamic_object_path.exists():
        print(f"Error: STEP file not found: {dynamic_object_path}")
        return 1
    
    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        return 1
    
    with open(config_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if len(lines) < 2:
        print("Error: Config file must contain at least 2 lines: samples and max displacement")
        return 1
    
    try:
        number_of_samples = int(lines[0])
        max_displacement = float(lines[1])
        number_of_proses = int(lines[2])
        gmsh_path = lines[3]
        elmer_grid_path = lines[4]
        elmer_solver_path = lines[5]

    except ValueError as e:
        print(f"Error parsing config file: {e}")
        return 1
    
    if number_of_samples < 2:
        print("Error: Number of samples must be at least 2")
        return 1
    
    print("Configuration:")
    print(f"  Samples: {number_of_samples}")
    print(f"  Max displacement: {max_displacement} units")
    print(f"  number of prossesrs: {number_of_proses}")
    
    print("Loading original STEP file...")
    try:
        original_object = cq.importers.importStep(str(dynamic_object_path))
        print("  Loaded successfully")
    except Exception as e:
        print(f"Error loading STEP file: {e}")
        return 1
    
    output_dir = Path("displaced_objects")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    
    displacement_step = max_displacement / (number_of_samples - 1)
    print(f"Displacement step: {displacement_step} units")
    
    list_of_dir_str = []
    list_of_mesh = []
    list_of_dir = []

    for i in range(number_of_samples):
        displacement = displacement_step * i
        
        print(f"Processing displacement {i+1}/{number_of_samples}: {displacement:.3f} units")
        
        displacement_str = f"{displacement:.6f}".replace('.', '_')
        folder_path = output_dir / f"disp_{displacement_str}"
        folder_path.mkdir(parents=True, exist_ok=True)
        
        translated_object = original_object.translate((0, 0, displacement))
        
        output_path = folder_path / "pasiveElement.step"
        
        shutil.copy("./electromagPayload.geo", folder_path / "electromagPayload.geo")
        shutil.copy("./coil.step", folder_path / "coil.step")
        shutil.copy("./backplain.step", folder_path / "backplain.step")
        shutil.copy("./autorun.sif", folder_path / "case.sif")
        
        try:
            cq.exporters.export(translated_object, str(output_path))
            print(f"  Saved STEP to: {output_path}")
        except Exception as e:
            print(f"  Error saving: {e}")
            return 1
        
        print(f"  Running Gmsh in: {folder_path}")
        result = subprocess.run(
            [gmsh_path, "-3", "electromagPayload.geo", "-o", "output.msh"],
            cwd=folder_path,
            capture_output=True,
            text=True)
        
        if result.returncode == 0:
            print(f"  Gmsh completed successfully")
        else:
            print(f"  Gmsh failed: {result.stderr}")
            return 1

        list_of_dir_str.append(str(folder_path))
        list_of_dir.append(folder_path)
        list_of_mesh.append("output.msh")
    print(f"\nComplete! Generated {number_of_samples} displaced objects in '{output_dir}/'")

    elmer.execute.run_multicore(number_of_proses, list_of_dir_str, list_of_mesh, elmer_grid_path, elmer_solver_path)

    magnetic_energy = []

    for i in range(number_of_samples):
        with open(list_of_dir[i] / "magnetic_energy.dat", 'r') as text:
            magnetic_energy.append(float(text.read().split()[0]))
        print(magnetic_energy[i])

    force = []

    for i in range(number_of_samples):
        if i != 0:
            force.append((magnetic_energy[i] - magnetic_energy[i-1])/displacement_step)
        else:
            force.append(float('nan'))
        print(force[i])

    return 0


if __name__ == "__main__":
    exit(main())