#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 10:05:33 2019

@author: mfau
"""


import h5py
import numpy as np

class H5Object(object):
    pass

class H5Attributes(object):
    pass

class h5Wrapper(H5Object):
    @classmethod
    def from_file(cls, fileName):
        obj = cls()
        obj.loadFile(fileName)

        return obj

    @classmethod
    def from_metadata(cls, dataType, dataWriter, writerVersion, examDate, patientName, serieNumber):
        obj = cls()
        obj.setMetaData(dataType, dataWriter, writerVersion, examDate, patientName, serieNumber)

        return obj

    def __init__(self):
        H5Object.__init__(self)

    def setMetaData(self, dataType, dataWriter, writerVersion, examDate, patientName, serieNumber):
        self.attributes = H5Object()
        self.attributes.DATA_TYPE = dataType
        self.attributes.DATA_WRITER = dataWriter
        self.attributes.PLUGIN_SHA1 = writerVersion
        self.attributes.examDate = examDate
        self.attributes.patientName = patientName
        self.attributes.serieNumber = serieNumber

    def loadFile(self, fileName):
        handle = h5py.File(fileName, 'r')
        h5Wrapper.__convertFromH5(handle, self)
        handle.close()

    def saveFile(self, filename):
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
                    if hasattr(value, 'attributes'):
                        for attr2, value2 in value.attributes.__dict__.items():
                            handle2.attrs[attr2] = value2
                else:
                    handle2 = handle.create_group(attr)
                    cls.__convertToH5(handle2, value)
