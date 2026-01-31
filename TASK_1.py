import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------------------------------------------
# Load input data
# ------------------------------------------------------------

print("Loading input files...")

import sys
sys.path.append('.')

from node import nodes
from element import members

print(f"Nodes loaded   : {len(nodes)}")
print(f"Elements loaded: {len(members)}")

ds = xr.open_dataset(r'./screening_task.nc')

print("Xarray dataset loaded")
print("Available components:", ds['Component'].values)

# ------------------------------------------------------------
# Central longitudinal girder definition
# ------------------------------------------------------------

central_elements = [15, 24, 33, 42, 51, 60, 69, 78, 83]

print("\nCentral girder elements:", central_elements)

# Check continuity of the central girder
for i, ele in enumerate(central_elements):
    ni, nj = members[ele]
    if i > 0:
        prev_nj = members[central_elements[i - 1]][1]
        if ni != prev_nj:
            print("Warning: element connectivity issue at element", ele)

print("Central girder connectivity verified")

# ------------------------------------------------------------
# Extract bending moment and shear force values
# ------------------------------------------------------------

positions = []
bending_moments = []
shear_forces = []

print("\nExtracting Mz and Vy for central girder...")

for idx, ele in enumerate(central_elements):

    node_i = members[ele][0]
    node_j = members[ele][1]

    coord_i = nodes[node_i]
    coord_j = nodes[node_j]

    # position along girder (x direction)
    pos_i = coord_i[0]
    pos_j = coord_j[0]

    try:
        mz_i = float(ds['forces'].sel(Element=ele, Component='Mz_i').values)
        mz_j = float(ds['forces'].sel(Element=ele, Component='Mz_j').values)
        vy_i = float(ds['forces'].sel(Element=ele, Component='Vy_i').values)
        vy_j = float(ds['forces'].sel(Element=ele, Component='Vy_j').values)
    except KeyError as e:
        print("Error reading element", ele)
        print("Available components:", ds['Component'].values)
        raise

    if idx == 0:
        positions.extend([pos_i, pos_j])
        bending_moments.extend([mz_i, mz_j])
        shear_forces.extend([vy_i, vy_j])
    else:
        positions.append(pos_j)
        bending_moments.append(mz_j)
        shear_forces.append(vy_j)

positions = np.array(positions)
bending_moments = np.array(bending_moments)
shear_forces = np.array(shear_forces)

print("Extraction completed")
print("Number of points:", len(positions))

# ------------------------------------------------------------
# Plot SFD and BMD
# ------------------------------------------------------------

import mplcursors

fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# -----------------------
# Bending moment diagram
# -----------------------

ax_bmd = axes[0]
line_bmd, = ax_bmd.plot(
    positions,
    bending_moments,
    marker='o',
    linewidth=2.5
)

ax_bmd.fill_between(positions, bending_moments, alpha=0.3)
ax_bmd.axhline(0, linewidth=1.2)
ax_bmd.grid(True, linestyle='--', alpha=0.6)

ax_bmd.set_ylabel("Bending Moment (kNm)", fontsize=12)
ax_bmd.set_title(
    "Bending Moment Diagram (BMD)\nCentral Longitudinal Girder",
    fontsize=14,
    fontweight='bold'
)

# -----------------------
# Shear force diagram
# -----------------------

ax_sfd = axes[1]
line_sfd, = ax_sfd.plot(
    positions,
    shear_forces,
    marker='o',
    linewidth=2.5,
    color="#C476CA"
)

ax_sfd.fill_between(positions, shear_forces, color="#C476CA", alpha=0.3)
ax_sfd.axhline(0, linewidth=1.2)
ax_sfd.grid(True, linestyle='--', alpha=0.6)

ax_sfd.set_xlabel("Position along Girder (m)", fontsize=12)
ax_sfd.set_ylabel("Shear Force (kN)", fontsize=12)
ax_sfd.set_title(
    "Shear Force Diagram (SFD)",
    fontsize=14,
    fontweight='bold'
)

# ------------------------------------------------------------
# Interactive hover values
# ------------------------------------------------------------

cursor_bmd = mplcursors.cursor(line_bmd, hover=True)
cursor_sfd = mplcursors.cursor(line_sfd, hover=True)

@cursor_bmd.connect("add")
def on_add_bmd(sel):
    x, y = sel.target
    sel.annotation.set_text(
        f"Position: {x:.2f} m\nMoment: {y:.2f} kNm"
    )
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

@cursor_sfd.connect("add")
def on_add_sfd(sel):
    x, y = sel.target
    sel.annotation.set_text(
        f"Position: {x:.2f} m\nShear: {y:.2f} kN"
    )
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

plt.tight_layout()
plt.show()
