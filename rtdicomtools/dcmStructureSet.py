import cv2
import pydicom
import numpy as np
from pydicom.pixel_data_handlers import apply_rescale

class StructureSetContour:
    """A class to store the relevant countour information of a RTStruct structure.
    """
    
    def __init__(self, name:str, color:tuple, contours:list, slices:list) -> None:
        """Initializes the StrucutrSetContour class.

        Args:
            name (str): Name of the structure.
            color (tuple): RGB color of the structure.
            contours (list): Contours of the structure.
            slices (list): Slice indices of the structure.
        """
        
        self.Name = name
        self.Color = color
        self.ContourSequence = contours
        self.Slices = slices
    
    def getName(self) -> str:
        """Get the name of the structure.

        Returns:
            str: Name of the structure.
        """
        return self.Name	
    
    def getColor(self) -> tuple:
        """Get the color of the structure.

        Returns:
            tuple: RGB color of the structure.
        """
        return self.Color
    
    def getContours(self) -> list:
        """Get the contour sequence of the structure.

        Returns:
            list: Contour sequence of the structure.
        """
        return self.ContourSequence	
    
    def getSlices(self) -> list:
        """Get the slice indices of the structure.

        Returns:
            list: Slice indices of the structure.
        """
        return self.Slices
    
class DICOMStructureSet:   
    """A class to handle structures in DICOM RTSTRUCT files.
    Structures and corresponding contours can be extrancted and manipulated without the need for the corresponding CT.
    If a CT is supplied, the underlying pixel array of the CT can be used to draw the contours on the CT slices.
    """ 	
    
    def __init__(self, RTStruct, CT: list = None, ignore_for: bool = False) -> None:
        """Initializes the DICOMStructureSet class.

        Args:
            RTStruct (pathlike or pydicom.FileDataset): The path to the DICOM RTSTRUCT file or the dataset containing the DICOM information.
            CT (list, optional): List of paths to the CT DICOM files. Defaults to None.
            ignore_for (bool, optional): Ignore the Frame of Reference check. Defaults to False.	
        """
        
        if type(RTStruct) == str:
            ds = pydicom.dcmread(RTStruct)
        elif type(RTStruct) == pydicom.FileDataset:
            ds = RTStruct
        else:
            raise TypeError("The input must be a path to the DICOM RTSTRUCT file or the dataset containing the DICOM information.")
        
        if ds.Modality != "RTSTRUCT":
            raise TypeError("The file is not a DICOM RTSTRUCT file")
        
        if CT != None:
            referenced_images = [i.ReferencedSOPInstanceUID for i in ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].ContourImageSequence]
            reference_images = {}
            self.image_position_patients = []
            for file in CT:
                if isinstance(file, str):
                    ct = pydicom.dcmread(file)
                else:
                    ct = file

                f = lambda x : 51*x/160 + 459/4

                
                array = apply_rescale(ct.pixel_array.copy(), ct)
                array[array <= -360 ] = -360
                array[array >= 440] = 440
                array = f(array)
                array = array.astype(int)
                reference_images[int(ct.InstanceNumber)-1] = (ct.SOPInstanceUID, array, ct.ImagePositionPatient[2])
                self.image_position_patients.append(ct.ImagePositionPatient[2])
            if set(referenced_images) != set([i[0] for i in reference_images.values()]) and ignore_for == False:
                raise ValueError("The CTs do not match the RTSTRUCT file.")
            self.slices = []
            flip = reference_images[min(reference_images.keys())][2] > reference_images[max(reference_images.keys())][2]
            for key in sorted(reference_images.keys(), reverse= flip):
                self.slices.append(reference_images[key][1])
            
            self.slices = np.array(self.slices, dtype=np.uint8)

            self._image_width = self.slices.shape[2]
            self._image_height = self.slices.shape[1]
            self._dimensions = (self._image_width, self._image_height, 3)
            self._pixel_spacing = 1/ct.PixelSpacing[0]
            self._center = (-1*int(ct.ImagePositionPatient[0]/ct.PixelSpacing[0]), -1*int(ct.ImagePositionPatient[1]/ct.PixelSpacing[1]))
        else:
            
            self._image_width = 512
            self._image_height = 512
            self._dimensions = (self._image_width, self._image_height, 3)
            self._pixel_spacing = 1

        self._AvailableStructures = self._setAvailableStructures(ds)
        self._StructureContours = self._setStructureContours(ds)
        self._Slices = self._setSlices()
        
    def __str__(self) -> str:
        """String representation of the DICOMStructureSet object.

        Returns:
            str: String representation.
        """
        name = self.__class__.__name__
        number_of_structures = f"Number of structures: {len(self.getAvailableStructureNames())}"
        available_structures = f"Available structures: {', '.join(self.getAvailableStructureNames())}"
        
        return_string = f"{name}\n\n{number_of_structures}\n{available_structures}"
        return return_string
    
    
    def _setAvailableStructures(self, ds: pydicom.FileDataset) -> dict:
        """Initializes the dictionaty which contains the available structures.

        Args:
            ds (pydicom.FileDataset): Dataset containing the DICOM information.

        Returns:
            dict: Dictionary which containts the structures available in the structure set.
        """
        available_structures = {}
        for i in range(len(ds.StructureSetROISequence)):
            try:
                if ds.ROIContourSequence[i].ContourSequence[0].ContourGeometricType == "CLOSED_PLANAR":
                    ROIName = ds.StructureSetROISequence[i].ROIName
                    ROINumber = ds.StructureSetROISequence[i].ROINumber
                    available_structures[ROIName] = ROINumber	
            except AttributeError as e: print(e)
            
        return available_structures
            
    def _setStructureContours(self, ds: pydicom.FileDataset) -> dict:
        """Initializes the dictionary which contains the contours of the structures.

        Args:
            ds (pydicom.FileDataset): Dataset containing the DICOM information.

        Returns:
            dict: Dictionary which contains the contours of the structures.	
        """
        structure_contours = {}
        for i in range(len(ds.StructureSetROISequence)):
            try: 
                name = ds.StructureSetROISequence[i].ROIName
                color = ds.ROIContourSequence[i].ROIDisplayColor
                contours =  [ ds.ROIContourSequence[i].ContourSequence[j].ContourData 
                for j in range(len(ds.ROIContourSequence[i].ContourSequence))]
                slices = []
                for k in range(len(contours)):      
                    contours[k] = np.array(contours[k]).reshape(-1,3)
                    slices += [contours[k][0][2]]
                    contours[k] = contours[k][:,0:2]      
            
                structure_contours[name] = StructureSetContour(name, color, contours, slices)
            except AttributeError as e: print(e)
        return structure_contours
            
    def _setSlices(self) -> dict:
        """Initializes the dictionary which translates the slice number to the index of the array.

        Returns:
            dict: Dictionary which translates the slice number to the index of the array.	
        """
        
        """"""
        slices=[]
        for Structure in self.getAvailableStructureNames():
            for slice_number in self._StructureContours[Structure].getSlices():
                if slice_number not in slices:
                    slices.append(slice_number)
                    
        slices.sort()
        slice_dict = {x:i for i, x in enumerate(slices)}

        try:
            self.image_position_patients.sort()
            slice_dict = {x:i for i, x in enumerate(self.image_position_patients)}
        except AttributeError: pass
        
        return slice_dict

    def DrawAllContours(self, ct:bool = False, fill_ptv: str = None, resample:int = 1) -> np.ndarray:
        """Draw all the contours of all the structures in the structure set.
        
        Args:	
            ct (bool, optional): If the contours are drawn on a CT image. Defaults to False.

        Returns:
            np.ndarray: Array of the slices with the contours of all the structures.
        """
        if ct:
            center = self._center
            if resample > 1:
                self._pixel_spacing *= resample
                images = np.array([cv2.resize(np.array(cv2.cvtColor(i, cv2.COLOR_GRAY2RGB)), dsize=None, fx=resample, fy=resample, interpolation=cv2.INTER_LANCZOS4) for i in self.slices])
            else:
                images = np.array([np.array(cv2.cvtColor(image, cv2.COLOR_GRAY2RGB))for image in self.slices])
        else:
            images = [np.zeros(self._dimensions, dtype=np.uint8) for i in range(len(self._Slices))]

        if not ct:
            if hasattr(self, "_center")==False:
                n=images[0].shape
                center = (int(n[1]/2), int(n[0]/2))

                min_contour = 10000
                max_contour = -10000
                for s in self.getAvailableStructureNames():
                    min_contour = min(min_contour, np.min([min(points[:,1]) for points in self._StructureContours[s].getContours()]))
                    max_contour = max(max_contour, np.max([max(points[:,1]) for points in self._StructureContours[s].getContours()]))

                center = (int(n[1]/2), int(n[0]/2)-int((max_contour+min_contour)/2))
            else:
                center = self._center
    
        for Structure in self.getAvailableStructureNames():

            for contour, slice in zip(self._StructureContours[Structure].getContours(), self._StructureContours[Structure].getSlices()):
                points = np.array(contour* self.getPixelSpacing(), dtype=np.int32) 
                points[:,0] += center[0]*resample
                points[:,1] += center[1]*resample

                cv2.drawContours(images[self._Slices[slice]], [points], 0, self._StructureContours[Structure].getColor(), 1) 
                if fill_ptv != None:
                    if Structure == fill_ptv:
                        temp = images[self._Slices[slice]].copy()
                        cv2.fillPoly(temp, [points], self._StructureContours[Structure].getColor())
                        alpha = 0.7
                        frame_overlay=cv2.addWeighted(images[self._Slices[slice]], alpha, temp ,1-alpha, gamma=0)
                        images[self._Slices[slice]] = frame_overlay
        if resample > 1:
            self._pixel_spacing /= resample
        return np.array(images)
    
    def DrawStructureContours(self, Structure:str, RemoveEmptySlices:bool = True, ct:bool = False, fill:bool = False, fill_value= None) -> np.ndarray:
        """_summary_

        Args:
            Structure (str): Name if the Structure.
            RemoveEmptySlices (bool, optional): Restrict the output array size the the slices which
            contain the structure, or return all the slices. Defaults to True.
            ct (bool, optional): If the contours are drawn on a CT image. Defaults to False.	
            fill (bool, optional): Whether or not to fill the contour. Defaults to False.
            fill_value (int, optional): Value to fill the contour with. Defaults to None.

        Returns:
            np.ndarray: Array of the slices with the contours of the structure.	
        """
        
        if ct:
            images = self.slices.copy()
            center = self._center
            color = (255, 255, 255)
        else:
            images = [np.zeros(self._dimensions, dtype=np.uint8) for i in range(len(self._Slices))]
            if hasattr(self, "_center")==False:
                n=images[0].shape
                center = (int(n[1]/2), int(n[0]/2))

                min_contour = 10000
                max_contour = -10000
                for s in self.getAvailableStructureNames():
                    min_contour = min(min_contour, np.min([min(points[:,1]) for points in self._StructureContours[s].getContours()]))
                    max_contour = max(max_contour, np.max([max(points[:,1]) for points in self._StructureContours[s].getContours()]))

                #center = (int(n[1]/2), int(n[0]/2)-int((max_contour+min_contour)/2))
            else:
                center = self._center

            color = self._StructureContours[Structure].getColor()
            
        for contour, slice in zip(self._StructureContours[Structure].getContours(), self._StructureContours[Structure].getSlices()):
            points = np.array(contour* self.getPixelSpacing(), dtype=np.int32) 
            points[:,0] += center[0]
            points[:,1] += center[1]
    
            if fill: 
                if fill_value == None:
                    cv2.fillPoly(images[self._Slices[slice]], [points], color)
                else:
                    cv2.fillPoly(images[self._Slices[slice]], [points], fill_value)
            else: cv2.drawContours(images[self._Slices[slice]], [points], 0, color, 1) 

        if RemoveEmptySlices:
            images = [image for image in images if not np.all(image == 0)]

        return np.array(images)   
    
    
        
    def DrawStructureContourSlice(self, Structure: str, Slice:int, ct:bool = False) -> np.ndarray:
        """Draw the contours of a structure of a specific slice.

        Args:
            Structure (str): Name of the structure.
            Slice (int): Slice index.
            ct (bool, optional): If the contours are drawn on a CT image. Defaults to False.	

        Returns:
            np.ndarray: Array of the slice with the contours of the structure.
        """
            
        if ct:
            images = self.slices[Slice].copy()
            center = self._center
        else:
            image = np.zeros(self._dimensions, dtype=np.uint8)
            if hasattr(self, "_center")==False:
                n=images[0].shape
                center = (int(n[1]/2), int(n[0]/2))

                min_contour = 10000
                max_contour = -10000
                for s in self.getAvailableStructureNames():
                    min_contour = min(min_contour, np.min([min(points[:,1]) for points in self._StructureContours[s].getContours()]))
                    max_contour = max(max_contour, np.max([max(points[:,1]) for points in self._StructureContours[s].getContours()]))

                center = (int(n[1]/2), int(n[0]/2)-int((max_contour+min_contour)/2))
            else:
                center = self._center
            
        if Structure not in self.getAvailableStructureNames():
            raise ValueError("The specified structure is not available")
        
        if Slice not in self._Slices.keys():
            raise ValueError("The specified slice is not available")
        
        
            
        for contour, slice in zip(self._StructureContours[Structure].getContours(), self._StructureContours[Structure].getSlices()):
            if self._Slices[slice] == Slice:
                points = np.array(contour* self.getPixelSpacing(), dtype=np.int32) 
                points[:,0] += center[0]
                points[:,1] += center[1]
                cv2.drawContours(images[self._Slices[slice]], [points], 0, self._StructureContours[Structure].getColor(), 1)             
       
        return image	
        
    def getSliceIndices(self, Structure: str) -> list:
        """Get the indices of the slices that contain the specified structure.

        Args:
            Structure (str): Name of the structure.

        Returns:
            list: List of slice indices that contain the specified structure. 
        """
        indices = []
        for slice_number in self._StructureContours[Structure].getSlices():
            indices.append(self._Slices[slice_number])
        return indices
    	
    
    def setImageWidth(self, width: int) -> None:
        """Set the width of the output array in pixels.

        Args:
            width (int): Width in pixels.
        """
        if width > 0:
            self._image_width = width
            self._dimensions = (self.image_width, self.image_height, 3)    
        else:
            raise ValueError("^Width must be greater than 0")
        
    def getImageWidth(self) -> int:
        """Get the width of the output array in pixels.

        Returns:
            int: Width in pixels.
        """
        return self._image_width	   
        	
    def setImageHeight(self, height: int) -> None:
        """Set the height of the output array in pixels.

        Args:
            height (int): Height in pixels.
        """
        if height > 0:
            self._image_height = height	
            self._dimensions = (self._image_width, self._image_heigh, 3)	
        else:
            raise ValueError("Height must be greater that 0")
        
    def getImageHeight(self) -> int:
        """Get the height of the output array in pixels.

        Returns:
            int: Height in pixels.
        """
        return self._image_height	
    
    def setDimensions(self, width:int, height:int) -> None:
        """Set the dimensions of the output array in pixels.

        Args:
            width (int): Width in pixels.
            height (int): Height in pixels.
        """
        if width >0 and height > 0:
            self._image_width = width	
            self._image_height = height
            self._dimensions = (self._image_width, self._image_height, 3)	
        else:
            raise ValueError("Dimensions must be greater than 0")
        
    def getNumberOfSlices(self) -> int:
        """Get the number of slices contoured in the structure set.

        Returns:
            int: Number of slices contoured in the structure set.     
        """
        return len(self._Slices.keys())
        
    def getDimensions(self) -> tuple:
        """Get the dimensions of the output array in pixels.

        Returns:
            tuple: Dimensions in pixels.	
        """
        return (self._dimensions[0], self._dimensions[1])	
    
    def setPixelSpacing(self, x: int) -> None:
        if x > 0:
            self._pixel_spacing = x
        else:
            raise ValueError("Pixel spacing must be greater than 0")
        
    def getPixelSpacing(self) -> int:
        """Set the pixel spacing of the output array in pixels.

        Returns:
            int: Pixel spacing in pixels.		
        """
        return self._pixel_spacing	

    def getAvailableStructureNames(self) -> list:
        """Get a list of the structures in the structure set.

        Returns:
            list: All Structures in the structure set.
        """
        return list(self._AvailableStructures.keys())
    
