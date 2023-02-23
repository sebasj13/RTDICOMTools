# RTDICOMTools
My collection of Tools that extend the capabilities of current, widespread radiotherapy DICOM manipulation repositories.

# Table of Contents

- [Installation](#installation)
- [Available Classes](#available-classes)
    * [npViewer3D](#npviewer3d)
    * [dcmStructureSet](#dcmstructureset)
    * [dcmMLC](#dcmmlc)
    
## Installation

To use this repository, Python 3.8 or higher is required. To install the required packages, run the following command:

```console
pip install rtdicomtools
```

Then, you can import the classes from the repository:

```console
from rtdicomtools import *
```

<hr>

# npViewer3D

This class is initialized with a np.array of a 3D volume. The entries can either be scalars or RGB color values. One can then slice the volume in any desired diection. Also features a side-by-side view which shows the current slice marked with an indication line.
This class serves as the visuialization engine for some of the results produced by the other classes in this repository. Of course, it can also be used independently.

<hr>

# dcmStructureSet

This class is initialized with the path to a RTSTRUCT file. It can then be used to extract the structure names and their corresponding contours without the need for the referenced CT dataset. This is useful for when you have a RTSTRUCT file but not the CT dataset that it references - for example, when you have a RTSTRUCT file from a vendor that you want to use with a different treatment planning system, or patient privacy concerns prevent you from sharing the CT dataset.
If the CT dataset is available, the contours can be drawn in the same scale as the CT dataset. This is useful for when you want to visualize the contours on top of the CT dataset.

## Methods

Since the scale information is encoded in the referenced CT dataset, the contours are returned in an array of arbitrary dimensions. The scale can be adjusted later on, if the CT dataset is available. Check the documentation for methods that influence the grid size, spacing, etc.

### dcmStructureSet.DrawAllContours()

This method will draw all contours in the RTSTRUCT file. It will return a np.array of all contours, colored in the respective structure color.

### dcmStructureSet.DrawStructureContour(Structure, RemoveEmptySlices=True)

This method will draw all contours for the structure with the name `Structure`. It will return a np.array of all contours, colored in the respective structure color. If `RemoveEmptySlices` is set to True, it will remove any slices that do not contain any contours for the structure.

### dcmStructureSet.DrawStructureContourSlice(Structure, Slice)

This method will draw the contours for the structure with the name `Structure` of a specific slice.

### dcmStructureSet.getSliceIndices(Structure)

This method will return a list of all slice indices that contain contours for the structure

<hr>

# dcmMLC

This class is initialized with the path to a RTPLAN file. It can then be used to extract the MLC positions for each beam in the plan. Additionally, the MLC positions can be drawn, whether by control point, or the entire sequence. It also contains a method to find the centers of the MLC apertures.

## Methods

#### dcmMLC.DrawEntireMLCSequence(rotate=False, draw_edges=True)

This method will draw the entire MLC sequence. It will return a np.array of all MLC positions. If `rotate` is set to True, it will rotate the MLC positions by the collimator angle. If `draw_edges` is set to True, it will draw the edges of the MLC positions.

#### dcmMLC.DrawMLCAperture(beam, control_point, rotate=False, draw_edges=True)

This method will draw the MLC aperture for a specific beam and control point. It will return a np.array of all MLC positions. If `rotate` is set to True, it will rotate the MLC positions by the collimator angle. If `draw_edges` is set to True, it will draw the edges of the MLC positions.

#### dcmMLC.FindApertureCenters(beam, control_point, lower_area_bound, upper_area_bound)

This method will find the centers of the MLC apertures for a specific beam and control point. It will return a list of tuples, where each tuple contains the x and y coordinates of the center of the aperture. The `lower_area_bound` and `upper_area_bound` parameters are used to filter out apertures that are too small or too large.