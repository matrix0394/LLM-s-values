# Cultural Region Boundaries Feature

## Overview

This feature adds visual boundaries around cultural regions in the IVS cultural map (FigS1), making regional clustering more apparent. The boundaries are drawn using convex hull algorithm by default, with optional support for alpha shapes.

## Files Added/Modified

### New Files
- `analysis/si/boundary_utils.py` - Core boundary calculation and rendering functions
- `analysis/si/test_boundaries.py` - Test script for different configurations

### Modified Files
- `analysis/si/si_config.py` - Added boundary configuration constants
- `analysis/si/generate_figs1_cultural_map.py` - Integrated boundary rendering

## Usage

### Basic Usage (Default)

By default, boundaries are enabled with convex hull method:

```python
from si_config import load_ivs_data, FIGURES_DIR
from generate_figs1_cultural_map import generate_figs1_cultural_map

ivs_data = load_ivs_data()
output_dir = FIGURES_DIR / 'S1_IVS_cultural_map'
generate_figs1_cultural_map(ivs_data, output_dir)
```

### Disable Boundaries (Backward Compatibility)

To generate the map without boundaries (original behavior):

```python
generate_figs1_cultural_map(
    ivs_data, 
    output_dir,
    draw_boundaries=False
)
```

### With Filled Boundaries

To add transparent fill to boundaries:

```python
generate_figs1_cultural_map(
    ivs_data,
    output_dir,
    draw_boundaries=True,
    boundary_fill=True
)
```

### Using Alpha Shapes (Optional)

Alpha shapes provide more sophisticated concave boundaries. Requires `alphashape` library:

```bash
pip install alphashape
```

Then use:

```python
generate_figs1_cultural_map(
    ivs_data,
    output_dir,
    draw_boundaries=True,
    boundary_method='alpha_shape',
    boundary_alpha=2.0  # Adjust for tightness
)
```

## Configuration Parameters

The `generate_figs1_cultural_map()` function accepts the following boundary-related parameters:

- `draw_boundaries` (bool, default=True): Enable/disable boundary rendering
- `boundary_method` (str, default='convex_hull'): Boundary calculation method
  - `'convex_hull'`: Simple convex polygon (default, most robust)
  - `'alpha_shape'`: Concave boundary (requires alphashape library)
- `boundary_alpha` (float, default=0.0): Alpha parameter for alpha shapes
  - 0.0 = convex hull
  - Higher values = tighter, more concave boundaries
- `boundary_fill` (bool, default=False): Fill boundaries with transparent color

## Visual Styling

Boundary appearance is controlled by constants in `si_config.py`:

```python
BOUNDARY_LINE_WIDTH = 2.0      # Width of boundary lines
BOUNDARY_LINE_ALPHA = 0.5      # Transparency of boundary lines
BOUNDARY_FILL_ALPHA = 0.1      # Transparency of boundary fill
BOUNDARY_ZORDER = 1            # Rendering order (below points and labels)
BOUNDARY_MIN_POINTS = 3        # Minimum points needed for boundary
```

## Implementation Details

### Boundary Calculation

The `boundary_utils.py` module provides three main functions:

1. `calculate_convex_hull_boundary(points)` - Computes convex hull using scipy
2. `calculate_alpha_shape_boundary(points, alpha)` - Computes alpha shape (optional)
3. `calculate_region_boundary(points, method, alpha)` - Unified interface

### Error Handling

The implementation includes robust error handling:

- Regions with fewer than 3 points are skipped
- Invalid coordinates (NaN, Inf) are filtered out
- Calculation failures for individual regions don't stop the entire visualization
- Missing alphashape library falls back to convex hull
- Unsupported methods fall back to convex hull with warning

### Rendering Order (Z-Order)

Elements are rendered in this order (back to front):

1. Grid and axes (zorder=0)
2. Region boundaries (zorder=1)
3. Country points (zorder=2)
4. Country labels (zorder=3)

This ensures boundaries provide context without obscuring data.

## Testing

Run the test script to verify different configurations:

```bash
python3 analysis/si/test_boundaries.py
```

This generates three versions of the map:
1. With boundaries (default)
2. Without boundaries (backward compatibility)
3. With filled boundaries

## Examples

### Example 1: Default Configuration
```python
generate_figs1_cultural_map(ivs_data, output_dir)
```
- Boundaries enabled
- Convex hull method
- No fill
- Default styling

### Example 2: Custom Styling
```python
# Modify constants in si_config.py before importing
BOUNDARY_LINE_WIDTH = 3.0
BOUNDARY_LINE_ALPHA = 0.7

generate_figs1_cultural_map(ivs_data, output_dir)
```

### Example 3: Alpha Shapes with Fill
```python
generate_figs1_cultural_map(
    ivs_data,
    output_dir,
    boundary_method='alpha_shape',
    boundary_alpha=1.5,
    boundary_fill=True
)
```

## Troubleshooting

### Issue: Boundaries not appearing
- Check that `draw_boundaries=True` (default)
- Verify regions have at least 3 points
- Check console for warning messages

### Issue: Alpha shapes not working
- Install alphashape: `pip install alphashape`
- System will automatically fall back to convex hull if library is missing

### Issue: Boundaries look wrong
- Try adjusting `boundary_alpha` parameter for alpha shapes
- Check for data quality issues (NaN, Inf values)
- Verify cultural region assignments in data

## Future Enhancements

Possible future improvements:
- Density contour boundaries using KDE
- Per-region boundary method configuration
- Interactive boundary adjustment
- Boundary smoothing options

## References

- Scipy ConvexHull: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.ConvexHull.html
- Alpha Shapes: https://alphashape.readthedocs.io/
- WVS Cultural Map: https://www.worldvaluessurvey.org/
