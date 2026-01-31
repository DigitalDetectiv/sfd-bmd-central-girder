"""
Enhanced Bridge 3D Shear Force and Bending Moment Diagram Generator
MIDAS-style visualization with improved grids, borders, and pastel colors

with Fixed Girder Definitions and Visibility Controls
"""

import numpy as np
import xarray as xr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def create_enhanced_3d_diagram(nc_file, node_file, element_file, result_type='BMD', segments=50):
    """
    Create enhanced 3D diagram with:
    - CAD-style visible grids
    - Girder boundary edges
    - Pastel/muted colors for better visibility
    - Transparent surfaces
    - Proper girder visibility controls
    
    Parameters:
    -----------
    nc_file : str
        Path to NetCDF dataset
    node_file : str
        Path to node.py file
    element_file : str
        Path to element.py file
    result_type : str
        'BMD' or 'SFD'
    segments : int
        Number of segments per element (50 recommended)
    """
    
    print("\n" + "="*80)
    print(f"ENHANCED 3D {result_type} GENERATOR - Version 2.1")
    print("="*80 + "\n")
    
    # Load data
    print("📂 Loading data files...")
    ds = xr.open_dataset(nc_file)
    
    spec = {}
    with open(node_file, 'r') as f:
        exec(f.read(), spec)
    nodes = spec['nodes']
    
    spec = {}
    with open(element_file, 'r') as f:
        exec(f.read(), spec)
    members = spec['members']
    
    print(f"✓ Loaded: {len(nodes)} nodes, {len(members)} elements\n")
    
    # ========================================================================
    # DEFINE GIRDERS EXACTLY AS SPECIFIED IN TASK
    # ========================================================================
    girders = {
        'Girder 1': {
            'elements': [13, 22, 31, 40, 49, 58, 67, 76, 81],
            'nodes': [1, 11, 16, 21, 26, 31, 36, 41, 46, 6],
            'color': 'rgb(100, 149, 237)'  # Cornflower Blue
        },
        'Girder 2': {
            'elements': [14, 23, 32, 41, 50, 59, 68, 77, 82],
            'nodes': [2, 12, 17, 22, 27, 32, 37, 42, 47, 7],
            'color': 'rgb(127, 255, 212)'  # Aquamarine
        },
        'Girder 3': {
            'elements': [15, 24, 33, 42, 51, 60, 69, 78, 83],
            'nodes': [3, 13, 18, 23, 28, 33, 38, 43, 48, 8],
            'color': 'rgb(144, 238, 144)'  # Light Green
        },
        'Girder 4': {
            'elements': [16, 25, 34, 43, 52, 61, 70, 79, 84],
            'nodes': [4, 14, 19, 24, 29, 34, 39, 44, 49, 9],
            'color': 'rgb(255, 218, 120)'  # Pale Gold
        },
        'Girder 5': {
            'elements': [17, 26, 35, 44, 53, 62, 71, 80, 85],
            'nodes': [5, 15, 20, 25, 30, 35, 40, 45, 50, 10],
            'color': 'rgb(240, 128, 128)'  # Light Coral
        }
    }
    
    # Create reverse mapping: element_id -> girder_name
    element_to_girder = {}
    for girder_name, girder_info in girders.items():
        for eid in girder_info['elements']:
            element_to_girder[eid] = girder_name
    
    print(" Girder Definitions:")
    for gname, ginfo in girders.items():
        print(f"  {gname}: {len(ginfo['elements'])} elements")
    print()
    
    # Determine components
    if result_type == 'BMD':
        comp_i, comp_j = 'Mz_i', 'Mz_j'
        unit = 'kN·m'
        title = '3D Bending Moment Diagram (BMD) - Enhanced MIDAS Style'
        ylabel = 'Bending Moment'
    else:
        comp_i, comp_j = 'Vy_i', 'Vy_j'
        unit = 'kN'
        title = '3D Shear Force Diagram (SFD) - Enhanced MIDAS Style'
        ylabel = 'Shear Force'
    
    # Calculate scale
    print("Calculating scale factor...")
    all_values = []
    for eid in members.keys():
        try:
            val_i = abs(float(ds['forces'].sel(Element=eid, Component=comp_i).values))
            val_j = abs(float(ds['forces'].sel(Element=eid, Component=comp_j).values))
            all_values.extend([val_i, val_j])
        except:
            continue
    
    max_val = max(all_values) if all_values else 1.0
    scale = 1.8 / max_val if max_val > 0 else 1.0
    
    # Increase scale for SFD to make it more visible
    if result_type == "SFD":
        scale *= 3.0
    
    print(f"  Max {result_type}: {max_val:.2f} {unit}")
    print(f"  Scale factor: {scale:.6f}\n")
    
    # Create figure
    fig = go.Figure()
    
    # ENHANCED COLOR SCALE - Pastel/Muted tones
    colorscale = [
        [0.0, 'rgb(100, 149, 237)'],    # Cornflower Blue (soft blue)
        [0.25, 'rgb(127, 255, 212)'],   # Aquamarine (soft cyan)
        [0.5, 'rgb(144, 238, 144)'],    # Light Green (soft green)
        [0.75, 'rgb(255, 218, 120)'],   # Pale Gold (soft yellow)
        [1.0, 'rgb(240, 128, 128)']     # Light Coral (soft red)
    ]
    
    # Track trace indices for each girder
    girder_traces = {gname: [] for gname in girders.keys()}
    
    # Also add "Other Elements" category for transverse members
    girder_traces['Other Elements'] = []
    
    # ========================================================================
    # 1. DRAW ALL STRUCTURE CENTERLINES
    # ========================================================================
    print("Drawing structure centerlines...")
    for eid, (ni, nj) in members.items():
        x1, y1, z1 = nodes[ni]
        x2, y2, z2 = nodes[nj]
        
        # Determine which girder this element belongs to
        girder_name = element_to_girder.get(eid, 'Other Elements')
        
        trace = go.Scatter3d(
            x=[x1, x2],
            y=[y1, y2],
            z=[z1, z2],
            mode='lines',
            line=dict(
                color='rgba(20, 20, 20, 1.0)',
                width=6
            ),
            showlegend=False,
            hoverinfo='skip',
            name=girder_name,
            legendgroup=girder_name
        )
        
        fig.add_trace(trace)
        girder_traces[girder_name].append(len(fig.data) - 1)
    
    print(f" ✓ Drew {len(members)} centerlines\n")
    
    # ========================================================================
    # 2. CREATE FORCE/MOMENT SURFACES WITH BORDERS
    # ========================================================================
    print(f" Creating {result_type} surfaces with boundary edges...")
    element_count = 0
    
    # Track which girders we've shown in legend (to avoid duplicates)
    shown_in_legend = set()
    
    for eid, (ni, nj) in members.items():
        # Determine girder
        girder_name = element_to_girder.get(eid, 'Other Elements')
        
        try:
            x1, y1, z1 = nodes[ni]
            x2, y2, z2 = nodes[nj]
            
            v_i = float(ds['forces'].sel(Element=eid, Component=comp_i).values)
            v_j = float(ds['forces'].sel(Element=eid, Component=comp_j).values)
            
            # Create mesh surface
            X, Y, Z, C = [], [], [], []
            
            for i in range(segments + 1):
                t = i / segments
                
                x = x1 + t * (x2 - x1)
                y0 = y1 + t * (y2 - y1)   # Real girder transverse location
                z = z1 + t * (z2 - z1)
                
                v = v_i + t * (v_j - v_i)
                
                X.extend([x, x])
                Y.extend([y0, y0 + v * scale])   # Shifted by girder position
                Z.extend([z, z])
                C.extend([abs(v), abs(v)])
            
            # Create triangular mesh
            I, J, K = [], [], []
            for i in range(segments):
                b = i * 2
                I.extend([b, b + 1])
                J.extend([b + 1, b + 3])
                K.extend([b + 2, b + 2])
            
            # Show in legend only once per girder
            show_in_legend = girder_name not in shown_in_legend
            if show_in_legend:
                shown_in_legend.add(girder_name)
            
            # Add SEMI-TRANSPARENT mesh with enhanced lighting
            mesh = go.Mesh3d(
                x=X, y=Y, z=Z,
                i=I, j=J, k=K,
                
                name=girder_name,
                legendgroup=girder_name,
                showlegend=show_in_legend,
                
                intensity=C,
                colorscale=colorscale,
                cmin=min(all_values),
                cmax=max(all_values),
                opacity=0.75,
                showscale=(element_count == 0),
                colorbar=dict(
                    title=f"{result_type}<br>({unit})",
                    thickness=20,
                    len=0.7,
                    x=1.02
                ) if element_count == 0 else None,
                hovertemplate=(
                    f"<b>{girder_name} - Element {eid}</b><br>" +
                    f"Nodes: {ni} → {nj}<br>" +
                    f"{comp_i}: {v_i:.3f} {unit}<br>" +
                    f"{comp_j}: {v_j:.3f} {unit}<br>" +
                    "<extra></extra>"
                ),
                flatshading=False,
                lighting=dict(
                    ambient=0.7,
                    diffuse=0.8,
                    specular=0.3,
                    roughness=0.5,
                    fresnel=0.2
                ),
                lightposition=dict(x=1000, y=1000, z=1000)
            )
            
            fig.add_trace(mesh)
            girder_traces[girder_name].append(len(fig.data) - 1)
            
            # ADD BOUNDARY EDGES at element ends
            # Start edge (vertical)
            edge = go.Scatter3d(
                x=[x1, x1],
                y=[y1, y1 + v_i * scale],
                z=[z1, z1],
                mode='lines',
                line=dict(
                    color='rgba(0, 0, 0, 0.9)',
                    width=4
                ),
                showlegend=False,
                hoverinfo='skip',
                name=girder_name,
                legendgroup=girder_name
            )
            fig.add_trace(edge)
            girder_traces[girder_name].append(len(fig.data) - 1)
            
            # End edge (vertical)
            edge = go.Scatter3d(
                x=[x2, x2],
                y=[y2, y2 + v_j * scale],
                z=[z2, z2],
                mode='lines',
                line=dict(
                    color='rgba(0, 0, 0, 0.9)',
                    width=2
                ),
                showlegend=False,
                hoverinfo='skip',
                name=girder_name,
                legendgroup=girder_name
            )
            fig.add_trace(edge)
            girder_traces[girder_name].append(len(fig.data) - 1)
            
            # Top edge (horizontal connecting peaks)
            edge = go.Scatter3d(
                x=[x1, x2],
                y=[y1 + v_i * scale, y2 + v_j * scale],
                z=[z1, z2],
                mode='lines',
                line=dict(
                    color='rgba(0, 0, 0, 0.9)',
                    width=1.5
                ),
                showlegend=False,
                hoverinfo='skip',
                name=girder_name,
                legendgroup=girder_name
            )
            fig.add_trace(edge)
            girder_traces[girder_name].append(len(fig.data) - 1)
            
            element_count += 1
            
        except Exception as e:
            print(f" Warning: Could not process element {eid}: {e}")
            continue
    
    print(f"  ✓ Created {element_count} surfaces with boundary edges\n")
    
    # ========================================================================
    # 3. ENHANCED LAYOUT with CAD-STYLE GRIDS
    # ========================================================================
    print("Applying CAD-style grid and styling...\n")
    
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Arial, sans-serif'}
        },
        scene=dict(
            # X-AXIS with visible grid
            xaxis=dict(
                title=dict(text='X (m)', font=dict(size=14, color='#34495e')),
                gridcolor='rgb(180, 180, 180)',
                gridwidth=2,
                showgrid=True,
                zeroline=True,
                zerolinecolor='rgb(100, 100, 100)',
                zerolinewidth=3,
                showbackground=True,
                backgroundcolor='rgb(245, 245, 250)',
                showspikes=False,
                dtick=2.5,
                tickfont=dict(size=11)
            ),
            # Y-AXIS with visible grid
            yaxis=dict(
                title=dict(text=f'{ylabel} ({unit})', font=dict(size=14, color='#34495e')),
                gridcolor='rgb(180, 180, 180)',
                gridwidth=2,
                showgrid=True,
                zeroline=True,
                zerolinecolor='rgb(100, 100, 100)',
                zerolinewidth=3,
                showbackground=True,
                backgroundcolor='rgb(245, 245, 250)',
                showspikes=False,
                tickfont=dict(size=11)
            ),
            # Z-AXIS with visible grid
            zaxis=dict(
                title=dict(text='Z (m)', font=dict(size=14, color='#34495e')),
                gridcolor='rgb(180, 180, 180)',
                gridwidth=2,
                showgrid=True,
                zeroline=True,
                zerolinecolor='rgb(100, 100, 100)',
                zerolinewidth=3,
                showbackground=True,
                backgroundcolor='rgb(245, 245, 250)',
                showspikes=False,
                dtick=2.0,
                tickfont=dict(size=11)
            ),
            aspectratio=dict(x=2, y=1, z=1),
            camera=dict(
                eye=dict(x=1.8, y=1.5, z=1.2),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=1, z=0)
            ),
            bgcolor='rgb(250, 250, 252)'
        ),
        width=1600,
        height=900,
        margin=dict(l=0, r=100, b=0, t=80),
        paper_bgcolor='rgb(255, 255, 255)',
        font=dict(family='Arial, sans-serif', size=12, color='#2c3e50'),
        hovermode='closest'
    )
    
    # ========================================================================
    # 4. ADD VISIBILITY CONTROL BUTTONS
    # ========================================================================
    print(" Adding girder visibility controls...\n")
    
    buttons = []
    total_traces = len(fig.data)
    
    # Button: Show All
    buttons.append(dict(
        label="All Girders",
        method="update",
        args=[{"visible": [True] * total_traces}]
    ))
    
    # Button for each girder
    for girder_name in ['Girder 1', 'Girder 2', 'Girder 3', 'Girder 4', 'Girder 5']:
        if girder_name in girder_traces:
            visibility = [False] * total_traces
            for idx in girder_traces[girder_name]:
                visibility[idx] = True
            
            buttons.append(dict(
                label=girder_name,
                method="update",
                args=[{"visible": visibility}]
            ))
    
    # Button: Show only transverse members
    if 'Other Elements' in girder_traces and girder_traces['Other Elements']:
        visibility = [False] * total_traces
        for idx in girder_traces['Other Elements']:
            visibility[idx] = True
        
        buttons.append(dict(
            label="Transverse Only",
            method="update",
            args=[{"visible": visibility}]
        ))
    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="down",
                buttons=buttons,
                x=0.01,
                y=0.99,
                xanchor='left',
                yanchor='top',
                showactive=True,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='rgba(0, 0, 0, 0.3)',
                borderwidth=1
            )
        ]
    )
    
    
    print(f"ENHANCED 3D {result_type} COMPLETE")
   
    
    return fig


def main():
    """Main execution"""
    print("\n" + "="*80)
    print("ENHANCED BRIDGE 3D DIAGRAMS ")
    print("Improved Grids | Visible Borders | Pastel Colors | Girder Controls")
    print("="*80 + "\n")
    
    # Check files
    nc_file = r'./screening_task.nc'
    node_file = r'./node.py'
    element_file = r'./element.py'
    
    for f in [nc_file, node_file, element_file]:
        if not Path(f).exists():
            print(f" Error: File not found: {f}")
            return
    
    print("✓ All input files found\n")
    
    # Create BMD
    print("="*80)
    print("GENERATING BENDING MOMENT DIAGRAM (BMD)")
    print("="*80)
    bmd_fig = create_enhanced_3d_diagram(nc_file, node_file, element_file, 'BMD', segments=50)
    
    # Save and show
    output_bmd = 'Enhanced_BMD_3D.html'
    bmd_fig.write_html(output_bmd)
    print(f"Saved: {output_bmd}")
    bmd_fig.show()
    
    # Create SFD
    print("\n" + "="*80)
    print("GENERATING SHEAR FORCE DIAGRAM (SFD)")
    print("="*80)
    sfd_fig = create_enhanced_3d_diagram(nc_file, node_file, element_file, 'SFD', segments=50)
    
    # Save and show
    output_sfd = 'Enhanced_SFD_3D.html'
    sfd_fig.write_html(output_sfd)
    print(f" Saved: {output_sfd}")
    sfd_fig.show()
    
   
    print("ALL ENHANCED DIAGRAMS COMPLETE")
    


if __name__ == "__main__":
    main()
