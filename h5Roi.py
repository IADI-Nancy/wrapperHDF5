#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:46:04 2019

@author: mfau
"""

from __future__ import annotations
from h5Wrapper import h5Wrapper, H5Object, H5Attributes
import numpy as np
import git
import os
import datetime
import random

class h5Roi(h5Wrapper):
    """
    Extends h5Wrapper to concatenate/separate ROI in a single array
    """
    
    @classmethod
    def from_file(cls, fileName: str) -> h5Roi:
        """
        Open a standardize ROI HDF5 file

        Parameters
        ----------
        fileName : str
            full path of file to open.

        Returns
        -------
        obj : h5Roi
            new object.

        """
        obj = cls()
        obj.loadFile(fileName)

        return obj

    @classmethod
    def from_metadata(cls, examDate: str, patientName: str, serieNumber: np.uint16, roiSize: list[np.uint16], pixelSpacing: list[float]) -> h5Roi:
        """
        Create an object with is minimal requirements

        Parameters
        ----------
        examDate : str
            Date of the exam (DD/MM/YYYY HH:mm).
        patientName : str
            Name of patient.
        serieNumber : np.uint16
            Number of serie in the acquisition.
        roiSize : list[np.uint16]
            Dimensions of ROI [x, y, z, t,...].
        pixelSpacing : list[float]
            Pixel Size of ROI [x, y, z, t,...].

        Returns
        -------
        obj : h5Roi
            new object.

        """
        
        obj = cls()
        repo = git.Repo(__file__ , search_parent_directories=True)
        obj.setMetaData("ROI", "python", repo.head.object.hexsha, examDate, patientName, serieNumber)
        obj.attributes.pixelSpacing = pixelSpacing
        obj.ROI = H5Object()
        obj.ROI.values = np.zeros(roiSize, dtype=np.uint64)
        obj.ROI.rois = []
        obj.ROI.attributes = H5Attributes()
        obj.ROI.attributes.colors = []
        obj.ROI.attributes.dates = []
        obj.ROI.attributes.names = []
        obj.ROI.attributes.operators = []
        obj.ROI.attributes.pows = []

        return obj

    def __init__(self):
        h5Wrapper.__init__(self)

    def loadFile(self, fileName: str) -> None:
        """
        Load standardized ROI HDF5 file into this object

        Parameters
        ----------
        fileName : str
            full path of file to open.

        """
        super().loadFile(fileName)
        if hasattr(self, "attributes") and hasattr(self.attributes, "DATA_TYPE") and self.attributes.DATA_TYPE == "ROI":
            self.__convertH5toRoi()
        else:
            print("The opened file is not a ROI")

    def saveFile(self, fileName: str) -> None:
        """
        Dump current object inta a file

        Parameters
        ----------
        fileName : str
            full path of file to save.
        """
        self.__convertRoiToH5()
        super().saveFile(fileName)

    def addRoi(self, name: str, operator: str = "", date: str = "", color: str = "") -> None:
        if operator == "":
            operator = getUserName()

        if date == "":
            date =  datetime.date.now().strftime("%Y/%m/%d %H:%M:%S")

        if color == "":
            color = "#"
            color += "%0.2X" % (random() * 255)
            color += "%0.2X" % (random() * 255)
            color += "%0.2X" % (random() * 255)
            color += "80"

        self.ROI.attributes.colors.append(color)
        self.ROI.attributes.dates.append(date)
        self.ROI.attributes.names.append(name)
        self.ROI.attributes.operators.append(operator)

        pows = self.ROI.attributes.pows.copy()
        pows.sort()
        ipow = 0;
        for i in range(64):
            if i >= len(pows) or i != pows[i]:
                ipow = i
                break

        self.ROI.attributes.pows.append(ipow)
        self.ROI.rois.append(np.zeros(self.ROI.values.shape, dtype=np.bool))
        
        return ipow

    def removeRoi(self, ipow) -> None:
        index  = -1
        for tmpIPow, tmpPow in enumerate(self.ROI.attributes.pows):
            if tmpPow == ipow:
                index = tmpIPow;
                break
        
        del self.ROI.attributes.colors[index]
        del self.ROI.attributes.dates[index]
        del self.ROI.attributes.names[index]
        del self.ROI.attributes.operators[index]
        del self.ROI.rois[index]
        del self.ROI.attributes.pows[index]

    def __convertH5toRoi(self):
        self.ROI.rois = []
        for nPow in self.ROI.attributes.pows :
            self.ROI.rois.append(np.bitwise_and(self.ROI.values, 1 << nPow).astype(bool))

    def __convertRoiToH5(self):
        self.ROI.values.fill(0)
        for iPow, nPow in enumerate(self.ROI.attributes.pows) :
            self.ROI.values = np.bitwise_or(self.ROI.values, self.ROI.rois[iPow] << nPow)

def getUserName() -> str:
    user = os.environ.get('USERNAME')
    if user == "":
        user = os.environ.get('USER')

    return user