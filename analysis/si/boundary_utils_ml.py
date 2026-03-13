"""
Machine Learning-based boundary calculation for cultural regions.

This module uses classification algorithms (SVM, Random Forest, k-NN) to create
smooth, non-overlapping decision boundaries between cultural regions, similar to
the approach used in the model_cultural_comp project.

The key advantage is that decision boundaries are naturally non-overlapping and
can be smoothly visualized using contour plots.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder


def train_region_classifier(
    data: pd.DataFrame,
    method: str = 'svm',
    **kwargs
) -> Tuple[object, LabelEncoder]:
    """
    Train a classifier to predict cultural regions from PC coordinates.
    
    Args:
        data: DataFrame with columns ['PC1', 'PC2', 'cultural_region']
        method: Classification method
                - 'svm': Support Vector Machine (default, smooth boundaries)
                - 'rf': Random Forest (more complex boundaries)
                - 'knn': k-Nearest Neighbors (local boundaries)
        **kwargs: Additional parameters for the classifier
        
    Returns:
        Tuple of (trained_classifier, label_encoder)
    """
    # Prepare data
    X = data[['PC1', 'PC2']].values
    y = data['cultural_region'].values
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Select and train classifier
    if method == 'svm':
        # SVM with RBF kernel for smooth boundaries
        clf = SVC(
            kernel=kwargs.get('kernel', 'rbf'),
            C=kwargs.get('C', 10.0),
            gamma=kwargs.get('gamma', 'scale'),
            probability=True
        )
    elif method == 'rf':
        # Random Forest for more complex boundaries
        clf = RandomForestClassifier(
            n_estimators=kwargs.get('n_estimators', 100),
            max_depth=kwargs.get('max_depth', 10),
            random_state=kwargs.get('random_state', 42)
        )
    elif method == 'knn':
        # k-NN for local boundaries
        clf = KNeighborsClassifier(
            n_neighbors=kwargs.get('n_neighbors', 5),
            weights=kwargs.get('weights', 'distance')
        )
    else:
        raise ValueError(f"Unsupported method: {method}. Use 'svm', 'rf', or 'knn'")
    
    # Train classifier
    clf.fit(X, y_encoded)
    
    return clf, le


def create_decision_boundary_mesh(
    xlim: Tuple[float, float],
    ylim: Tuple[float, float],
    resolution: int = 200
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a mesh grid for decision boundary visualization.
    
    Args:
        xlim: (min, max) for x-axis (PC1)
        ylim: (min, max) for y-axis (PC2)
        resolution: Number of points in each dimension
        
    Returns:
        Tuple of (xx, yy) mesh grid arrays
    """
    x_min, x_max = xlim
    y_min, y_max = ylim
    
    # Add padding
    x_padding = (x_max - x_min) * 0.05
    y_padding = (y_max - y_min) * 0.05
    
    xx, yy = np.meshgrid(
        np.linspace(x_min - x_padding, x_max + x_padding, resolution),
        np.linspace(y_min - y_padding, y_max + y_padding, resolution)
    )
    
    return xx, yy


def plot_decision_boundaries(
    ax: plt.Axes,
    clf: object,
    le: LabelEncoder,
    xx: np.ndarray,
    yy: np.ndarray,
    region_colors: dict,
    alpha: float = 0.3
) -> None:
    """
    Plot decision boundaries as filled contours (fills entire space).
    
    Args:
        ax: Matplotlib axes object
        clf: Trained classifier
        le: Label encoder
        xx: X mesh grid
        yy: Y mesh grid
        region_colors: Dictionary mapping region names to colors
        alpha: Transparency of filled regions
    """
    # Predict on mesh grid
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    # Get unique labels and their colors
    unique_labels = np.unique(Z)
    region_names = le.inverse_transform(unique_labels)
    
    # Create color list for contourf
    colors = [region_colors.get(name, '#DDDDDD') for name in region_names]
    
    # Plot filled contours
    contour = ax.contourf(
        xx, yy, Z,
        levels=np.arange(len(unique_labels) + 1) - 0.5,
        colors=colors,
        alpha=alpha
    )
    
    return contour


def plot_decision_boundaries_masked(
    ax: plt.Axes,
    clf: object,
    le: LabelEncoder,
    xx: np.ndarray,
    yy: np.ndarray,
    data: pd.DataFrame,
    region_colors: dict,
    alpha: float = 0.3,
    mask_padding: float = 0.3,
    smooth_boundary: bool = True
) -> None:
    """
    Plot decision boundaries only around actual data points (masked).
    
    This creates a more natural look by only showing boundaries where
    there is actual data, rather than filling the entire space.
    The outer boundaries are smoothed using spline interpolation for
    a more organic, hand-drawn appearance like WVS maps.
    
    Args:
        ax: Matplotlib axes object
        clf: Trained classifier
        le: Label encoder
        xx: X mesh grid
        yy: Y mesh grid
        data: Original data with PC1, PC2, cultural_region columns
        region_colors: Dictionary mapping region names to colors
        alpha: Transparency of filled regions
        mask_padding: Padding around convex hulls for masking
        smooth_boundary: Whether to smooth the outer boundaries with splines
    """
    from scipy.spatial import ConvexHull
    from scipy.interpolate import splprep, splev
    from matplotlib.path import Path as MplPath
    
    # Predict on mesh grid
    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    
    # Create a mask: only show boundaries near actual data points
    mask = np.zeros_like(Z, dtype=bool)
    smoothed_hulls = {}  # Store smoothed hull boundaries for each region
    
    # For each region, create a convex hull and expand it slightly
    for region in data['cultural_region'].unique():
        if pd.isna(region):
            continue
            
        subset = data[data['cultural_region'] == region]
        points = subset[['PC1', 'PC2']].values
        
        if len(points) < 3:
            continue
        
        try:
            # Calculate convex hull
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            
            # Expand hull slightly
            center = points.mean(axis=0)
            expanded_hull = center + (hull_points - center) * (1 + mask_padding)
            
            # Smooth the expanded hull boundary if requested
            if smooth_boundary and len(expanded_hull) >= 4:
                try:
                    # Close the boundary loop
                    closed_hull = np.vstack([expanded_hull, expanded_hull[0]])
                    
                    # Apply B-spline smoothing with lower smoothing factor
                    # to preserve the expanded boundary size
                    tck, u = splprep([closed_hull[:, 0], closed_hull[:, 1]], 
                                    s=0.2, per=True, k=min(3, len(expanded_hull)-1))
                    
                    # Evaluate at many points for smooth curve
                    u_new = np.linspace(0, 1, 100)
                    smooth_x, smooth_y = splev(u_new, tck)
                    smoothed_hull = np.column_stack([smooth_x, smooth_y])
                    
                    smoothed_hulls[region] = smoothed_hull
                    expanded_hull = smoothed_hull
                except Exception as e:
                    print(f"Warning: Smoothing failed for {region}, using original hull: {e}")
            
            # Create path and check which grid points are inside
            path = MplPath(expanded_hull)
            grid_points = np.c_[xx.ravel(), yy.ravel()]
            inside = path.contains_points(grid_points)
            mask = mask | inside.reshape(xx.shape)
        except Exception as e:
            print(f"Warning: Hull calculation failed for {region}: {e}")
            continue
    
    # Apply mask to Z
    Z_masked = np.ma.masked_where(~mask, Z)
    
    # Get unique labels and their colors
    unique_labels = np.unique(Z[mask])
    region_names = le.inverse_transform(unique_labels)
    
    # Create color list for contourf
    colors = [region_colors.get(name, '#DDDDDD') for name in region_names]
    
    # Plot filled contours (only in masked regions)
    contour = ax.contourf(
        xx, yy, Z_masked,
        levels=np.arange(len(unique_labels) + 1) - 0.5,
        colors=colors,
        alpha=alpha
    )
    
    return contour


def plot_smooth_decision_boundaries(
    ax: plt.Axes,
    clf: object,
    le: LabelEncoder,
    xx: np.ndarray,
    yy: np.ndarray,
    region_colors: dict,
    alpha: float = 0.3,
    n_levels: int = 20
) -> None:
    """
    Plot smooth decision boundaries using probability contours.
    
    This creates smoother transitions between regions by using
    prediction probabilities instead of hard classifications.
    
    Args:
        ax: Matplotlib axes object
        clf: Trained classifier with probability support
        le: Label encoder
        xx: X mesh grid
        yy: Y mesh grid
        region_colors: Dictionary mapping region names to colors
        alpha: Transparency of filled regions
        n_levels: Number of contour levels for smoothness
    """
    if not hasattr(clf, 'predict_proba'):
        # Fall back to regular decision boundaries
        return plot_decision_boundaries(ax, clf, le, xx, yy, region_colors, alpha)
    
    # Get probabilities for each class
    Z_proba = clf.predict_proba(np.c_[xx.ravel(), yy.ravel()])
    
    # For each region, plot its probability contours
    for i, region_name in enumerate(le.classes_):
        Z_region = Z_proba[:, i].reshape(xx.shape)
        color = region_colors.get(region_name, '#DDDDDD')
        
        # Plot filled contours for this region
        ax.contourf(
            xx, yy, Z_region,
            levels=np.linspace(0, 1, n_levels),
            colors=[color],
            alpha=alpha * Z_region.max()  # Scale alpha by max probability
        )


def generate_ml_boundaries(
    data: pd.DataFrame,
    region_colors: dict,
    method: str = 'svm',
    resolution: int = 200,
    **kwargs
) -> Tuple[object, LabelEncoder, np.ndarray, np.ndarray]:
    """
    Generate ML-based decision boundaries for cultural regions.
    
    This is the main interface for creating smooth, non-overlapping
    region boundaries using machine learning classifiers.
    
    Args:
        data: DataFrame with columns ['PC1', 'PC2', 'cultural_region']
        region_colors: Dictionary mapping region names to colors
        method: Classification method ('svm', 'rf', 'knn')
        resolution: Mesh grid resolution
        **kwargs: Additional classifier parameters
        
    Returns:
        Tuple of (classifier, label_encoder, xx_mesh, yy_mesh)
    """
    # Train classifier
    clf, le = train_region_classifier(data, method=method, **kwargs)
    
    # Create mesh grid
    xlim = (data['PC1'].min(), data['PC1'].max())
    ylim = (data['PC2'].min(), data['PC2'].max())
    xx, yy = create_decision_boundary_mesh(xlim, ylim, resolution)
    
    return clf, le, xx, yy
