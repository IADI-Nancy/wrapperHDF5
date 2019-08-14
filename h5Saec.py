#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:08:02 2019

@author: mfau
"""

from h5Wrapper import h5Wrapper, H5Object, H5Attributes
import numpy as np
import pandas as pd

class h5Saec(h5Wrapper):
    @classmethod
    def from_file(cls, fileName):
        obj = cls()
        obj.loadFile(fileName)

        return obj

    def __init__(self):
        h5Wrapper.__init__(self)

    def loadFile(self, fileName, dataFrame=False):
        super().loadFile(fileName)
        if hasattr(self, "attributes") and hasattr(self.attributes, "DATA_TYPE") and self.attributes.DATA_TYPE == "SAEC":
            self.__convertH5toSaec(self, dataFrame)
        else:
            print("The opened file is not a SAEC data")

    def saveFile(self, fileName):
        print("This function is nos supported")


    @classmethod
    def __convertH5toSaec(cls, data, dataFrame=False):
        if dataFrame:
          if hasattr(data, "timestamp"):
            columns = ['timestamp']
            datas = data.timestamp.values;
            delattr(data.timestamp, "values")
    
            if hasattr(data, "datas"):
              #convert data from LSB to physical unit
              data.datas.values = data.datas.values.astype(float) * data.attributes.channelLSBValue + data.attributes.channelOffsetValue;
    
              columns.extend(data.datas.attributes.names)
              datas = np.append(datas, data.datas.values, axis=1)
              delattr(data.datas, "values")

    
            data.values = pd.DataFrame(datas, columns = columns)
    
            # last stage no need to go furtherer
            return data;
    
        for key, value in data.__dict__.items():
            if key != "attributes" and key != "timestamp":
                if key == "datas":
                  #convert data from LSB to physical unit
                  value.values = value.values.astype(float) * data.attributes.channelLSBValue + data.attributes.channelOffsetValue;
                else:
                    value = cls.__convertH5toSaec(value, dataFrame);
    
        return data