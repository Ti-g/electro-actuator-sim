SetFactory("OpenCASCADE");

coil() = ShapeFromFile("coil.step");
backplain() = ShapeFromFile("backplain.step");
pasiv() = ShapeFromFile("pasiveElement.step");

coil_vol = coil();
backplain_vol = backplain();
pasiv_vol = pasiv();

coil_surfaces[] = Boundary{ Volume{coil_vol}; };
backplain_surfaces[] = Boundary{ Volume{backplain_vol}; };
pasiv_surfaces[] = Boundary{ Volume{pasiv_vol}; };

Characteristic Length{ coil_surfaces[] } = 3;
Characteristic Length{ backplain_surfaces[] } = 3;
Characteristic Length{ pasiv_surfaces[] } = 3;

Box(4) = {-400, -400, -400, 800, 800, 800};

BooleanDifference(5) = { Volume{4}; Delete; }{ Volume{coil(), backplain(), pasiv()}; };

Coherence;

Physical Volume("coil_volume") = {coil()};
Physical Volume("backplain_volume") = {backplain()};
Physical Volume("pasive_volume") = {pasiv()};
Physical Volume("air_volume") = {5};

Mesh.CharacteristicLengthMax = 60;