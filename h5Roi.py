#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:46:04 2019

@author: mfau
"""

from h5Wrapper import h5Wrapper, H5Object, H5Attributes
import numpy as np
import git
import os
import datetime
import random

class h5Roi(h5Wrapper):
    @classmethod
    def from_file(cls, fileName):
        obj = cls()
        obj.loadFile(fileName)

        return obj

    @classmethod
    def from_metadata(cls, examDate, patientName, serieNumber, roiSize, pixelSpacing):
        obj = cls()
        repo = git.Repo(search_parent_directories=True)
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

    def loadFile(self, fileName):
        super().loadFile(fileName)
        if hasattr(self, "attributes") and hasattr(self.attributes, "DATA_TYPE") and self.attributes.DATA_TYPE == "ROI":
            self.__convertH5toRoi()
        else:
            print("The opened file is not a ROI")

    def saveFile(self, fileName):
        self.__convertRoiToH5()
        super().saveFile(fileName)

    def addRoi(self, name, mask, operator = "", date = "", color = ""):
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

        pows = self.ROI.attributes.pows.deepcopy()
        pows.sort()
        ipow = 0;
        for i in range(64):
            if i - 1 >= pows.len() or i != pows[i]:
                ipow = i
                break

        self.ROI.attributes.pows.append(ipow)

    def removeRoi(self, index):
        del self.ROI.attributes.colors[index]
        del self.ROI.attributes.dates[index]
        del self.ROI.attributes.names[index]
        del self.ROI.attributes.operators[index]
        del self.ROI.attributes.pows[index]

    def __convertH5toRoi(self):
        self.ROI.rois = []
        for nPow in self.ROI.attributes.pows :
            self.ROI.rois.append(np.bitwise_and(self.ROI.values, 1 << nPow).astype(bool))

    def __convertRoiToH5(self):
        self.ROI.values.fill(0)
        for iPow, nPow in enumerate(self.ROI.attributes.pows) :
            self.ROI.values = np.bitwise_or(self.ROI.values, self.ROI.rois[iPow] << nPow)

def getUserName():
    user = os.environ.get('USERNAME')
    if user == "":
        user = os.environ.get('USER')

    return user