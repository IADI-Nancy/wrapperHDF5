# -*- coding: utf-8 -*-
"""
Created on Thu May 20 14:56:51 2021

@author: mfau
"""

import wfdb
import os
import numpy as np
from h5Saec import *

def convert(oldPath: str, newPath: str, serieNumber : int = 1):
    oldData = wfdb.rdrecord(oldPath)
    
    newData = h5Saec.from_metadata(oldData.base_datetime.strftime("%Y/%m/%d %H:%M:%S"), oldData.recordName, serieNumber)
    currentDevice = newData.addDevice(newData, "DEVICE", "WFDB", "1")
    
    precSPF = 0
    precUnit = ""
    precADCGain = 0.0
    precADCOffset = 0.0
    precADCRes = 0.0
    precFreq = 0
    sensorType = ""
    channelsNames = []
    startIndex = 0
    for i in range(len(oldData.sig_name)):
        if precSPF != oldData.samps_per_frame[i] or precUnit != oldData.units[i]  or precADCGain != oldData.adc_gain[i] or precADCRes != oldData.adc_res[i]:
            if startIndex != 0:
                sensorType = os.path.commonprefix(channelsNames)
                
                currentSensor = newData.addSensor(
                    currentDevice, 
                    sensorType, 
                    sensorType, 
                    sensorType,
                    precUnit,
                    precFreq, 
                    precADCRes, 
                    [e[len(sensorType) - 1:] for e in channelsNames] if len(channelsNames) > 1 else channelsNames, 
                    precADCGain, 
                    precADCOffset
                )
                currentSensor.getattr(sensorType).datas.values = oldData.p_record[:, startIndex: i-1]
                currentSensor.getattr(sensorType).timestamps.values = np.linspace(0, len(oldData.p_record) / (precFreq / oldData.fs), oldData.fs / precFreq).astype(np.uint64)
            
            channelsNames = []
            precSPF = oldData.samps_per_frame[i]
            precUnit = oldData.units[i]
            precADCGain = oldData.adc_gain[i]
            precADCOffset = oldData.adc_zero[i]
            precADCRes = oldData.adc_res[i]
            precFreq = oldData.samps_per_frame[i] * oldData.fs
            startIndex = i
            
        channelsNames.append(oldData.sig_name[i])
        
    sensorType = os.path.commonprefix(channelsNames)
                
    currentSensor = newData.addSensor(
        currentDevice, 
        sensorType, 
        sensorType, 
        sensorType,
        precUnit,
        precFreq, 
        precADCRes, 
        [e[len(sensorType) - 1:] for e in channelsNames] if len(channelsNames) > 1 else channelsNames, 
        precADCGain, 
        precADCOffset
    )
    currentSensor.getattr(sensorType).datas.values = oldData.p_record[:, startIndex: i-1]
    currentSensor.getattr(sensorType).timestamps.values = np.linspace(0, len(oldData.p_record) / (precFreq / oldData.fs), oldData.fs / precFreq).astype(np.uint64)
    
    newData.saveFile(newPath)