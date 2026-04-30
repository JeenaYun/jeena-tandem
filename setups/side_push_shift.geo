SetFactory("OpenCASCADE");

res = 50.0;
res_surf = 0.5;
res_f = 2.0;
res_f_dd = 10.0;
slab_curvature = 3.0/1000;

z0 = -0.5;
x0 = Sqrt(-z0/slab_curvature);
H = 15;
h = 3;
Wf = 40;

Xmin = -400; 
Ymin = -200;
Xmax = Sqrt(-(Ymin + z0)/slab_curvature) - x0 - Xmin;

Point(1) = {Xmin, 0.0, 0.0, res};
Point(2) = {Xmax, 0.0, 0.0, res};
Point(3) = {Xmax, Ymin, 0.0, res};
Point(4) = {Xmin, Ymin, 0.0, res};
Point(111) = {20, 0.0, 0.0, res_f};

Point(11) = {0.0, 0.0, 0.0, res_f};
Point(12) = {Sqrt(-(-5+z0)/slab_curvature) - x0, -5, 0.0, res_f};
Point(13) = {Sqrt(-(-10+z0)/slab_curvature) - x0, -10, 0.0, res_f};
Point(14) = {Sqrt(-(0.125*Ymin+z0)/slab_curvature) - x0, 0.125*Ymin, 0.0, res_f};
Point(15) = {Sqrt(-(0.25*Ymin+z0)/slab_curvature) - x0, 0.25*Ymin, 0.0, res_f};
Point(16) = {Sqrt(-(0.5*Ymin+z0)/slab_curvature) - x0, 0.5*Ymin, 0.0, res_f};
Point(17) = {Sqrt(-(0.75*Ymin+z0)/slab_curvature) - x0, 0.75*Ymin, 0.0, res_f};
Point(18) = {Sqrt(-(Ymin+z0)/slab_curvature) - x0, Ymin, 0.0, res_f};

// Create domain
Line(1) = {1, 11};
Line(2) = {11, 111};
Line(3) = {111, 2};
Line(4) = {2, 3};
Line(5) = {3, 18};
Line(6) = {18, 4};
Line(7) = {4, 1};

// Deine intersection lines for split
Point(1000) = {Sqrt((H+z0)/slab_curvature) - x0 - 10, -H, 0.0, res_f};
Point(1001) = {Sqrt((H+z0)/slab_curvature) - x0 + 10, -H, 0.0, res_f};
Line(11) = {1000, 1001};
Point(1002) = {Sqrt((H+h+z0)/slab_curvature) - x0 - 10, -(H+h), 0.0, res_f};
Point(1003) = {Sqrt((H+h+z0)/slab_curvature) - x0 + 10, -(H+h), 0.0, res_f};
Line(12) = {1002, 1003};
Point(1004) = {Sqrt((Wf+z0)/slab_curvature) - x0 - 10, -Wf, 0.0, res_f};
Point(1005) = {Sqrt((Wf+z0)/slab_curvature) - x0 + 10, -Wf, 0.0, res_f};
Line(13) = {1004, 1005};

// Create main fault
Spline(100) = {11, 12, 13, 14, 15, 16, 17, 18};

// Split the curve into multiple segments
rsf_fault() = BooleanFragments{ Line{100, 11, 12, 13}; Delete; }{};

// Control resolution
MeshSize {11, 111} = res_surf;
MeshSize {112, 113} = res_f;
MeshSize {114} = res_f_dd;
MeshSize {18} = res/2;
// MeshSize {16} = res/2;

Curve Loop(1) = {8, 9, 10, 11, -5, -4, -3, -2};
Curve Loop(2) = {8, 9, 10, 11, 6, 7, 1};

// Deine physical quantities
Plane Surface(1) = {1};
Plane Surface(2) = {2};
Physical Curve(1) = {1, 2, 3, 5, 6};
Physical Curve(3) = {8, 9, 10, 11};
Physical Curve(5) = {4, 7};
Physical Surface(1) = {1};
Physical Surface(2) = {2};
Mesh.MshFileVersion = 2.2;