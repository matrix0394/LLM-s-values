"""
Boundary calculation utilities for cultural region visualization.

This module provides functions to calculate and render boundaries around
cultural regions in PCA space, supporting multiple boundary algorithms:
- Convex hull (default, using scipy)
- Alpha shapes (optional, requires alphashape library)
- Voronoi regions (non-overlapping, based on region centroids)
- Smooth boundaries using spline interpolation

The boundaries enhance visualization by making regional clustering more apparent.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.path import Path
from typing import Optional, Dict, List, Tuple
from scipy.spatial import ConvexHull, QhullError, Voronoi, voronoi_plot_2d
from scipy.interpolate import splprep, splev

# Check for optional alphashape library
try:
    import alphashape
    ALPHASHAPE_AVAILABLE = True
except ImportError:
    ALPHASHAPE_AVAILABLE = False


def smooth_boundary(boundary: np.ndarray, smoothing_factor: float = 0.3, num_points: int = 100) -> np.ndarray:
    """
    Smooth a boundary using B-spline interpolation.
    
    This creates smooth, curved boundaries similar to hand-drawn maps
    by fitting a B-spline curve through the boundary vertices.
    
    Args:
        boundary: Mx2 numpy array of boundary vertices
        smoothing_factor: Smoothing parameter (0=no smoothing, higher=more smooth)
                         Typical range: 0.1-1.0
        num_points: Number of points in the smoothed curve (higher=smoother)
        
    Returns:
        Nx2 numpy array of smoothed boundary vertices
    """
    if boundary is None or len(boundary) < 3:
        return boundary
    
    try:
        # Close the boundary loop
        closed_boundary = np.vstack([boundary, boundary[0]])
        
        # Parametric B-spline interpolation
        # s=smoothing_factor controls how closely the spline follows the points
        # k=3 uses cubic splines for smooth curves
        tck, u = splprep([closed_boundary[:, 0], closed_boundary[:, 1]], 
                         s=smoothing_factor, per=True, k=min(3, len(boundary)-1))
        
        # Evaluate the spline at many points for a smooth curve
        u_new = np.linspace(0, 1, num_points)
        smooth_x, smooth_y = splev(u_new, tck)
        
        return np.column_stack([smooth_x, smooth_y])
    except Exception as e:
        print(f"Warning: Boundary smoothing failed: {e}, using original boundary")
        return boundary


def calculate_convex_hull_boundary(points: np.ndarray) -> Optional[np.ndarray]:
    """
    Calculate convex hull boundary for a set of 2D points.
    
    The convex hull is the smallest convex polygon that contains all points.
    This is the default and most robust boundary method.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates
        
    Returns:
        Mx2 numpy array of boundary vertices in counterclockwise order,
        or None if calculation fails or insufficient points
        
    Raises:
        ValueError: If points array has invalid shape (not 2D coordinates)
    """
    # Validate input shape
    if len(points.shape) != 2 or points.shape[1] != 2:
        raise ValueError(f"Points must be Nx2 array, got shape {points.shape}")
    
    # Check for insufficient points
    if points.shape[0] < 3:
        return None
    
    # Filter out invalid coordinates (NaN, Inf)
    valid_mask = np.all(np.isfinite(points), axis=1)
    if not np.all(valid_mask):
        points = points[valid_mask]
        if points.shape[0] < 3:
            return None
    
    try:
        # Calculate convex hull
        hull = ConvexHull(points)
        # Extract vertices in order (counterclockwise for 2D)
        boundary_vertices = points[hull.vertices]
        return boundary_vertices
    except (QhullError, Exception) as e:
        # Log warning and return None for graceful degradation
        print(f"Warning: Convex hull calculation failed: {e}")
        return None


def calculate_alpha_shape_boundary(points: np.ndarray, alpha: float = 0.0) -> Optional[np.ndarray]:
    """
    Calculate alpha shape (concave hull) boundary for a set of 2D points.
    
    Alpha shapes provide more sophisticated boundaries that can handle
    concave regions. Requires the alphashape library.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates
        alpha: Alpha parameter controlling boundary tightness
               - alpha = 0: convex hull (default)
               - larger alpha: tighter, more concave boundaries
        
    Returns:
        Mx2 numpy array of boundary vertices in order,
        or None if calculation fails or library unavailable
        
    Note:
        Falls back to convex hull if alphashape library is not available
        or if alpha shape calculation fails.
    """
    # Check library availability
    if not ALPHASHAPE_AVAILABLE:
        print("Warning: alphashape library not installed, falling back to convex hull")
        print("Install with: pip install alphashape")
        return calculate_convex_hull_boundary(points)
    
    # Validate input
    if len(points.shape) != 2 or points.shape[1] != 2:
        raise ValueError(f"Points must be Nx2 array, got shape {points.shape}")
    
    if points.shape[0] < 3:
        return None
    
    # Filter out invalid coordinates
    valid_mask = np.all(np.isfinite(points), axis=1)
    if not np.all(valid_mask):
        points = points[valid_mask]
        if points.shape[0] < 3:
            return None
    
    try:
        # Calculate alpha shape
        alpha_shape = alphashape.alphashape(points, alpha)
        
        # Extract boundary coordinates from shapely polygon
        if hasattr(alpha_shape, 'geom_type'):
            if alpha_shape.geom_type == 'Polygon':
                boundary_coords = np.array(alpha_shape.exterior.coords)
                return boundary_coords
            else:
                # MultiPolygon or other complex geometry - fall back to convex hull
                print(f"Warning: Alpha shape returned {alpha_shape.geom_type}, falling back to convex hull")
                return calculate_convex_hull_boundary(points)
        else:
            # Unexpected return type
            print("Warning: Alpha shape returned unexpected type, falling back to convex hull")
            return calculate_convex_hull_boundary(points)
            
    except Exception as e:
        print(f"Warning: Alpha shape calculation failed: {e}")
        return calculate_convex_hull_boundary(points)


def calculate_region_boundary(
    points: np.ndarray,
    method: str = 'convex_hull',
    alpha: float = 0.0,
    smooth: bool = True,
    smoothing_factor: float = 0.3
) -> Optional[np.ndarray]:
    """
    Calculate boundary for a region using specified method.
    
    This is the main interface for boundary calculation, dispatching to
    the appropriate algorithm based on the method parameter.
    
    Args:
        points: Nx2 numpy array of (x, y) coordinates
        method: Boundary calculation method
                - 'convex_hull': Convex hull (default, most robust)
                - 'alpha_shape': Alpha shape (requires alphashape library)
        alpha: Alpha parameter for alpha shapes (ignored for convex hull)
        smooth: Whether to apply spline smoothing to the boundary
        smoothing_factor: Smoothing parameter for spline (0.1-1.0, default 0.3)
        
    Returns:
        Mx2 numpy array of boundary vertices in order,
        or None if calculation fails
        
    Note:
        Unsupported methods fall back to convex hull with a warning.
    """
    # Normalize method name
    method = method.lower().strip()
    
    # Calculate raw boundary
    if method == 'convex_hull':
        boundary = calculate_convex_hull_boundary(points)
    elif method == 'alpha_shape':
        boundary = calculate_alpha_shape_boundary(points, alpha)
    else:
        # Unsupported method - fall back to convex hull
        print(f"Warning: Unsupported boundary method '{method}', using convex hull")
        boundary = calculate_convex_hull_boundary(points)
    
    # Apply smoothing if requested
    if boundary is not None and smooth:
        boundary = smooth_boundary(boundary, smoothing_factor=smoothing_factor)
    
    return boundary


def plot_region_boundary(
    ax: plt.Axes,
    boundary: np.ndarray,
    color: str,
    line_width: float = 2.0,
    line_alpha: float = 0.5,
    fill: bool = False,
    fill_alpha: float = 0.1,
    zorder: int = 1
) -> None:
    """
    Plot a region boundary on matplotlib axes.
    
    Renders the boundary as a polygon patch with configurable styling.
    Supports both outline-only and filled polygons.
    
    Args:
        ax: Matplotlib axes object to plot on
        boundary: Mx2 numpy array of boundary vertices
        color: Color for boundary line and fill (matplotlib color spec)
        line_width: Width of boundary line in points
        line_alpha: Transparency of boundary line (0=transparent, 1=opaque)
        fill: Whether to fill the boundary polygon
        fill_alpha: Transparency of fill (0=transparent, 1=opaque)
        zorder: Z-order for rendering (lower values render behind)
        
    Note:
        When fill is enabled, both a filled polygon and an edge-only polygon
        are drawn to ensure the edge is visible with the specified line_alpha.
    """
    if boundary is None or len(boundary) < 3:
        return
    
    # Create filled polygon if requested
    if fill:
        filled_polygon = Polygon(
            boundary,
            closed=True,
            edgecolor='none',
            facecolor=color,
            linewidth=0,
            alpha=fill_alpha,
            fill=True,
            zorder=zorder
        )
        ax.add_patch(filled_polygon)
    
    # Create edge polygon (always drawn to show boundary line)
    edge_polygon = Polygon(
        boundary,
        closed=True,
        edgecolor=color,
        facecolor='none',
        linewidth=line_width,
        alpha=line_alpha,
        fill=False,
        zorder=zorder
    )
    ax.add_patch(edge_polygon)
