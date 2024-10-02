#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:05:33 2019

@author: mfau
"""

from __future__ import annotations
import h5py
import numpy as np
import time
import datetime

class WrongFileFormatError(Exception):
    pass

class H5Object(object):
    """
    A class used to represent an HDF5 Node
    """
    pass

class H5Attributes(object):
    """
    A class used to represent a list of HDF5 Attributes
    """
    pass

class h5Wrapper(H5Object):
    """
    A class used to standardize CIC-IT/IADI HDF5 structure and help handle it
    """
    
    @classmethod
    def from_file(cls, fileName: str) -> h5Wrapper:
        """
        Open a standardize HDF5 file

        Parameters
        ----------
        fileName : str
            full path of file to open.

        Returns
        -------
        h5Wrapper
            new object.
        """
        obj = cls()
        obj.loadFile(fileName)

        return obj

    @classmethod
    def from_metadata(cls, 
            dataType: str, 
            dataWriter: str, 
            writerVersion: str, 
            examDate: str, 
            patientName: str, 
            serieNumber: np.uint16
            ) -> h5Wrapper:
        """
        Create an object with is minimal requirements

        Parameters
        ----------
        dataType : str
            Type of global data (aka subclass).
        dataWriter : str
            Name of program that write datas.
        writerVersion : str
            Version of program that write datas.
        examDate : str
            Date of the exam (DD/MM/YYYY HH:mm).
        patientName : str
            Name of patient.
        serieNumber : np.uint16
            Number of serie in the acquisition.

        Returns
        -------
        h5Wrapper
            new object.
        """
        obj = cls()
        obj.setMetaData(dataType, dataWriter, writerVersion, examDate, patientName, serieNumber)

        return obj

    def __init__(self) -> None:
        H5Object.__init__(self)

    def setMetaData(self, 
            dataType: str, 
            dataWriter: str, 
            writerVersion: str, 
            examDate: str, 
            patientName: str, 
            serieNumber: np.uint16
            ) -> None:
        """
        Set minimal requirements

        Parameters
        ----------
        dataType : str
            Type of global data (aka subclass).
        dataWriter : str
            Name of program that write datas.
        writerVersion : str
            Version of program that write datas.
        examDate : str
            Date of the exam (DD/MM/YYYY HH:mm).
        patientName : str
            Name of patient.
        serieNumber : np.uint16
            Number of serie in the acquisition.
        """
        
        tmpTime = datetime.datetime.strptime(examDate, "%d/%m/%Y %H:%M:%S")
        
        self.attributes = H5Object()
        self.attributes.DATA_TYPE = dataType
        self.attributes.DATA_WRITER = dataWriter
        self.attributes.PLUGIN_SHA1 = writerVersion
        self.attributes.examDate = tmpTime.strftime("%Y%m%d-%H%M%S")
        self.attributes.examTimestamp = int(time.mktime(tmpTime.timetuple()))
        self.attributes.patientName = patientName
        self.attributes.serieNumber = np.uint16(serieNumber)

    def loadFile(self, fileName: str) -> None:
        """
        Load a file into current object

        Parameters
        ----------
        fileName : str
            full path of file to open.
        """
        handle = h5py.File(fileName, 'r')
        h5Wrapper.__convertFromH5(handle, self)
        handle.close()

    def saveFile(self, filename: str) -> None:
        """
        Dump current object inta a file

        Parameters
        ----------
         fileName : str
            full path of file to save.
        """
        handle = h5py.File(filename, "w")
        h5Wrapper.__convertToH5(handle, self);
        handle.close()

    @classmethod
    def __convertFromH5(cls, handle, data):
        data.attributes = H5Attributes()
        for item in handle.attrs.keys():
            attribute = handle.attrs[item]
            if isinstance(attribute, (bytes, bytearray)):
                attribute = attribute.decode("utf-8")
            elif type(attribute) is np.ndarray:
                for attrIndex, attrValue in enumerate(attribute):
                    if isinstance(attrValue, (bytes, bytearray)):
                        attribute[attrIndex] = attrValue.decode("utf-8")
            
            setattr(data.attributes, item, attribute)
        
        if isinstance(handle, h5py.Dataset):
            data.values = np.array(handle)
        else:
            for item in handle.keys():
                setattr(data, item, cls.__convertFromH5(handle[item], H5Object()))
            
        return data

    @classmethod
    def __convertToH5(cls, handle, data):
        for attr, value in data.__dict__.items():
            if attr == "attributes":
                for attr2, value2 in value.__dict__.items():
                    handle.attrs[attr2] = value2
            else :
                if hasattr(value, 'values'):
                    handle2 = handle.create_dataset(attr, data=value.values, compression="gzip", chunks=np.shape(value.values), compression_opts=9)
                elif hasattr(value, 'attributes'):
                    handle2 = handle.create_group(attr)

                if hasattr(value, 'attributes'):
                    cls.__convertToH5(handle2, value)
