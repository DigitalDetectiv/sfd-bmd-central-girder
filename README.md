
# Osdag Screening Task – SFD & BMD Visualization

This repository contains the solution for the **Osdag (FOSSEE, IIT Bombay) screening task**.

The project generates:

* **2D Shear Force and Bending Moment diagrams** for the central longitudinal girder
* **3D MIDAS-style Shear Force and Bending Moment diagrams** for all longitudinal girders

The results are extracted directly from a **NetCDF Xarray dataset** using Python.

---

## Project Title

**Generation of 2D and 3D Shear Force and Bending Moment Diagrams from Xarray Dataset using Python**

---

## Author

**Sneha Shaji**
4th Year B.Tech – School of Computing
VIT Bhopal University

---

## Input Files

The following files must be present in the same folder:

```
screening_task.nc
node.py
element.py
```

* `screening_task.nc` → Xarray NetCDF result file
* `node.py` → node coordinates dictionary
* `element.py` → element connectivity dictionary

---

## Task-1 : 2D SFD and BMD (Central Girder)

The 2D plots are generated for the central longitudinal girder using:

```
[15, 24, 33, 42, 51, 60, 69, 78, 83]
```

Features:

* Uses Matplotlib
* Continuous diagram along the girder
* Interactive hover values using `mplcursors`
* Uses dataset sign convention directly

Script:

```
Task_1.py   (or your 2D script file)
```

---

## Task-2 : 3D SFD and BMD (All Girders)

The 3D visualisation generates MIDAS-style diagrams for all longitudinal girders.

Features:

* Plotly based 3D interactive model
* Actual bridge geometry is used
* Force and moment values are shown as vertical extrusions
* Individual girder visibility controls
* Output saved as HTML files

Script:

```
3D_task_2.py
```

Output files generated:

```
Enhanced_BMD_3D.html
Enhanced_SFD_3D.html
```

---

## How to Run

Create a Python environment and install the required packages:

```
pip install numpy xarray matplotlib plotly mplcursors
```

Then run:

### For 2D diagrams

```
python Task_1.py
```

### For 3D diagrams

```
python 3D_task_2.py
```

---

## Notes

* The force components are taken directly from the dataset:

  * `Vy_i`, `Vy_j`
  * `Mz_i`, `Mz_j`
* No sign conversion is applied.
* The diagrams follow the sign convention present in the dataset.
* The 3D results are fully interactive through the generated HTML files.

---
