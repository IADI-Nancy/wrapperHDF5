#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 10:08:02 2019

@author: mfau
"""
from __future__ import annotations
from h5Wrapper import h5Wrapper, H5Object, H5Attributes, WrongFileFormatError
import numpy as np
import git #GitPython
import pandas as pd
import pathlib

class h5Saec(h5Wrapper):
    """
    Extends h5Wrapper to decode/encode ADC values into physical units
    """
    
    @classmethod
    def from_file(cls, fileName: str, dataFrame: bool = False) -> h5Saec:
        """
        Open a standardize SAEC HDF5 file

        Parameters
        ----------
        fileName : str
            full path of file to open.
        dataFrame : bool, optional
            Put data inside a pandas DataFrame. The default is False.

        Returns
        -------
        h5Saec
            new object.
        """
        obj = cls()
        obj.loadFile(fileName, dataFrame)

        return obj

    @classmethod
    def from_metadata(cls, examDate: str, patientName: str, serieNumber: np.uint16) -> h5Saec:
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

        Returns
        -------
        h5Saec
            new object.
        """
        obj = cls()
        repo = git.Repo(pathlib.Path(__file__).parent.resolve(), search_parent_directories=True)
        obj.setMetaData("SAEC", "python", repo.head.object.hexsha, examDate, patientName, serieNumber)
        obj.attributes.tickTo1s = np.uint64(1000000000)

        return obj

    def __init__(self) -> None:
        h5Wrapper.__init__(self)

    def loadFile(self, 
            fileName: str, 
            dataFrame : bool = False
            ) -> None:
        """
        Load standardized SAEC HDF5 file into this object

        Parameters
        ----------
        fileName : str
            full path of file to open.
        dataFrame : bool, optional
            Put data inside a pandas DataFrame. The default is False.

        """
        super().loadFile(fileName)
        if hasattr(self, "attributes") and hasattr(self.attributes, "DATA_TYPE") and self.attributes.DATA_TYPE == "SAEC":
            self.__convertH5toSaec(self, dataFrame)
        else:
            raise WrongFileFormatError("The opened file is not a SAEC data")

    def saveFile(self, fileName):
        """
        Dump current object inta a file

        Parameters
        ----------
         fileName : str
            full path of file to save.
        """
        self.__convertSaecToH5(self)
        super().saveFile(fileName)
        
    @classmethod
    def addDevice(cls, 
          parent: H5Object, 
          deviceType: str, 
          deviceName: str, 
          communicationId: str, 
          deviceProcessing : str = ""
          ) -> H5Object:
        """
        Add device with is minimal informations

        Parameters
        ----------
        parent : H5Object
            To add device.
        deviceType : str
            Type o device.
        deviceName : str
            Name of device.
        communicationId : str
            Communication id.
        deviceProcessing : str, optional
            processing Id (if processing). The default is "".

        Returns
        -------
        H5Object
            new device.

        """
        
        device = H5Object()
        device.attributes = H5Attributes()
        device.attributes.communicationId = communicationId
        device.attributes.deviceClass = deviceType
        device.attributes.deviceName = deviceName;
        device.attributes.deviceProcessing = deviceProcessing
        device.attributes.hardwareConfig = ""

        setattr(parent, deviceType + "_" + communicationId, device)

        return device
        
    @classmethod
    def addSensor(cls, 
            parent: H5Object, 
            senorType: str, 
            typeName: str, 
            typeUnit: str, 
            sensorName: str, 
            sensorFreq: np.uint32, 
            internalType: type, 
            sensorResolution: np.uint32, 
            channelsNames: list, 
            channelLSBValue: np.double, 
            channelOffsetValue: np.double, 
            channelMinValue : np.double = 0.0, 
            channelMaxValue : np.double = 0.0
            ) -> H5Object:
        """
        

        Parameters
        ----------
        parent : H5Object
            To add sensor.
        senorType : str
            Sensor type Id.
        typeName : str
            Type Name.
        typeUnit : str
            Type Unit.
        sensorName : str
            Sensor name.
        sensorFreq : np.uint32
            Sensor freq (0 if no frequency).
        internalType : type
            Type of variable containning ADC values (np.uint16 for exemple).
        sensorResolution : np.uint32
            Number of minimal bits to store ADC values.
        channelsNames : list
            Names of channels (if any).
        channelLSBValue : np.double
            LSB of ADC values.
        channelOffsetValue : np.double
            Offset of physical values.
        channelMinValue : np.double, optional
            Channels minimum value (to standardise charts). The default is 0.0.
        channelMaxValue : np.double, optional
             Channels maximum value (to standardise charts). The default is 0.0.

        Returns
        -------
        H5Object
            New sensor.

        """
        sensor = H5Object()
        sensor.attributes = H5Attributes()
        sensor.attributes.sensorType = senorType
        sensor.attributes.sensorName = sensorName
        sensor.attributes.channelLSBValue = channelLSBValue
        sensor.attributes.channelOffsetValue = channelOffsetValue
        sensor.attributes.channelMinValue = channelMinValue
        sensor.attributes.channelMaxValue = channelMaxValue
        sensor.attributes.sensorFreq = sensorFreq
        sensor.attributes.sensorResolution = sensorResolution
        sensor.attributes.typeName = typeName
        sensor.attributes.typeUnit = typeUnit
        
        if hasattr(parent.attributes, "hardwareConfig"):
            parent.attributes.hardwareConfig += "_" + senorType + str(len(channelsNames))
        
        sensor.timestamp = H5Object()
        sensor.timestamp.attributes = H5Attributes()
        sensor.timestamp.values = []
        
        sensor.datas = H5Object()
        sensor.datas.attributes = H5Attributes()
        sensor.datas.attributes.names = channelsNames
        sensor.datas.values = []
        sensor.datas.type = internalType
        
        setattr(parent, sensorName, sensor)
         
        return sensor


    @classmethod
    def __convertH5toSaec(cls, data: H5Object, dataFrame: bool = False) -> H5Object:
        if dataFrame:
          if hasattr(data, "timestamp"):
            columns = ['timestamp']
            datas = data.timestamp.values;
            delattr(data.timestamp, "values")
    
            if hasattr(data, "datas"):
              #convert data from LSB to physical unit
              data.datas.type = type(data.datas.values[0,0])
              data.datas.values = data.datas.values.astype(float) * data.attributes.channelLSBValue + data.attributes.channelOffsetValue
    
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
                  value.values = value.values.astype(float) * data.attributes.channelLSBValue + data.attributes.channelOffsetValue
                else:
                    value = cls.__convertH5toSaec(value, dataFrame)
    
        return data
    
    @classmethod
    def __convertSaecToH5(cls, data: H5Object) -> H5Object:
        for key, value in data.__dict__.items():
            if hasattr(value, "timestamp"):
                if hasattr(value, "values"):
                    value.timestamp.values = value.values.to_numpy()[:, 0:1].astype(np.uint64)
                    
                    if hasattr(value, "datas"):
                        value.datas.values = value.values.to_numpy()[:, 1:].astype(value.datas.type)
                        delattr(value.datas, "type")
                    
                    delattr(value, "values")
                    
                if hasattr(value, "datas"):
                    #convert data from physical unit to LSB
                    value.datas.values = (value.datas.values - value.attributes.channelOffsetValue) / value.attributes.channelLSBValue
            
            if hasattr(value, 'attributes'):
                h5Saec.__convertSaecToH5(value)

        return data