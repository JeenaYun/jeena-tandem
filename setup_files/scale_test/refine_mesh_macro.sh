gmsh -2 bp1.geo -order 2 -setnumber hf 10 -o bp1_base.msh
gmsh -refine bp1_base.msh -o bp1_refine1.msh
gmsh -refine bp1_refine1.msh -o bp1_refine2.msh
gmsh -refine bp1_refine2.msh -o bp1_refine3.msh
gmsh -refine bp1_refine3.msh -o bp1_refine4.msh