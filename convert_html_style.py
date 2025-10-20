#!/usr/bin/env python3
"""
Convert cultural map HTML file style to match the multilingual version
"""
import re
import json

# Read the source file
with open('/Users/yxy/code/LLM\'s values/results/roleplay_English/9_25/cultural_map_interactive.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the Plotly.newPlot call content
match = re.search(r'Plotly\.newPlot\([^,]+,\s*(\[.*?\]),\s*(\{.*?\}),\s*(\{.*?\})\s*\)', content, re.DOTALL)
if not match:
    print("Could not find Plotly.newPlot call")
    exit(1)

data_str = match.group(1)
layout_str = match.group(2)
config_str = match.group(3)

# Parse layout to modify it
# We'll do text replacements since full JSON parsing might fail due to JavaScript syntax
new_layout = layout_str

# Update title
new_layout = re.sub(
    r'"text":"\\u003cb\\u003eCultural Values Map: LLM Roleplay vs Real Countries\\u003c\\u002fb\\u003e',
    r'"text":"\\u003cb\\u003eCultural Values Map: LLM Roleplay vs Real Countries\\u003c\\u002fb\\u003e\\u003cbr\\u003e\\u003csub\\u003eInglehart-Welzel Framework \\u2022 Independent Legend Control\\u003c\\u002fsub\\u003e',
    new_layout
)

# Update xaxis title
new_layout = re.sub(
    r'"xaxis":\{"title":\{"text":"\\u003cb\\u003ePC1: Traditional vs Secular-Rational Values\\u003c\\u002fb\\u003e"',
    r'"xaxis":{"title":{"text":"\\u003cb\\u003ePC1: Survival vs Self-Expression Values\\u003c\\u002fb\\u003e"',
    new_layout
)

# Update yaxis title
new_layout = re.sub(
    r'"yaxis":\{"title":\{"text":"\\u003cb\\u003ePC2: Survival vs Self-Expression Values\\u003c\\u002fb\\u003e"',
    r'"yaxis":{"title":{"text":"\\u003cb\\u003ePC2: Traditional vs Secular-Rational Values\\u003c\\u002fb\\u003e"',
    new_layout
)

# Update dimensions
new_layout = re.sub(r'"width":1200', '"width":1500', new_layout)
new_layout = re.sub(r'"height":800', '"height":900', new_layout)

# Add margin if not exists, or update it
if '"margin"' in new_layout:
    new_layout = re.sub(r'"margin":\{[^}]+\}', '"margin":{"r":300}', new_layout)
else:
    # Add margin before width
    new_layout = re.sub(r'"width":', '"margin":{"r":300},"width":', new_layout)

# Update legend styling
new_layout = re.sub(
    r'"legend":\{"font":\{"size":10\}',
    r'"legend":{"font":{"size":11}',
    new_layout
)

# Add legend styling after the font size
new_layout = re.sub(
    r'("legend":\{"font":\{"size":11\},"orientation":"v","yanchor":"top","y":1,"xanchor":"left","x":1\.02)',
    r'\1,"bgcolor":"rgba(255,255,255,0.95)","bordercolor":"gray","borderwidth":1,"itemsizing":"constant"',
    new_layout
)

# Update corner annotations
new_layout = re.sub(
    r'"text":"\\u003cb\\u003eSecular-Rational\\u003cbr\\u003e& Self-Expression\\u003c\\u002fb\\u003e"',
    r'"text":"\\u003cb\\u003eSelf-Expression\\u003cbr\\u003e& Secular-Rational\\u003c\\u002fb\\u003e"',
    new_layout
)

new_layout = re.sub(
    r'"text":"\\u003cb\\u003eSecular-Rational\\u003cbr\\u003e& Survival\\u003c\\u002fb\\u003e"',
    r'"text":"\\u003cb\\u003eSurvival\\u003cbr\\u003e& Secular-Rational\\u003c\\u002fb\\u003e"',
    new_layout
)

new_layout = re.sub(
    r'"text":"\\u003cb\\u003eTraditional\\u003cbr\\u003e& Self-Expression\\u003c\\u002fb\\u003e"',
    r'"text":"\\u003cb\\u003eSelf-Expression\\u003cbr\\u003e& Traditional\\u003c\\u002fb\\u003e"',
    new_layout
)

new_layout = re.sub(
    r'"text":"\\u003cb\\u003eTraditional\\u003cbr\\u003e& Survival\\u003c\\u002fb\\u003e"',
    r'"text":"\\u003cb\\u003eSurvival\\u003cbr\\u003e& Traditional\\u003c\\u002fb\\u003e"',
    new_layout
)

# Update corner annotation positions for the new aspect ratio
# Right side annotations should be at x=0.75 instead of x=0.98 due to larger margin
new_layout = re.sub(
    r'("text":"\\u003cb\\u003eSelf-Expression\\u003cbr\\u003e& Traditional\\u003c\\u002fb\\u003e"[^}]+)"x":0\.98',
    r'\1"x":0.75',
    new_layout
)

new_layout = re.sub(
    r'("text":"\\u003cb\\u003eSurvival\\u003cbr\\u003e& Traditional\\u003c\\u002fb\\u003e"[^}]+)"x":0\.98',
    r'\1"x":0.75',
    new_layout
)

# Reconstruct the Plotly.newPlot call
new_plotly_call = f'Plotly.newPlot(\'f13d6e82-9a49-43e2-93a1-a5f8b0e72769\',{data_str},{new_layout},{config_str})'

# Replace in the original content
new_content = re.sub(
    r'Plotly\.newPlot\([^,]+,\s*\[.*?\],\s*\{.*?\},\s*\{.*?\}\s*\)',
    new_plotly_call,
    content,
    flags=re.DOTALL
)

# Write the new file
output_path = '/Users/yxy/code/LLM\'s values/results/roleplay_English/9_25/cultural_map_interactive_new_style.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"✅ Successfully created new styled file: {output_path}")
print(f"📊 Changes made:")
print(f"  - Updated title with subtitle")
print(f"  - Fixed incorrect axis labels (PC1 should be Survival↔Self-Expression, PC2 should be Traditional↔Secular)")
print(f"  - Increased dimensions to 1500x900")
print(f"  - Added right margin of 300px")
print(f"  - Enhanced legend styling with background and border")
print(f"  - Updated corner quadrant labels to match corrected axes")

