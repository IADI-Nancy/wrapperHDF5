function data = h5HeaderGen(dataType, dataWriter, writerVersion, examDate, patientName, serieNumber)
% h5HeaderGen generata a minimal HDF5 header compatible with ArchiMed3
% data = h5HeaderGen(dataType, dataWriter, writerVersion, examDate, patientName, serieNumber)
% dataType : Type of data (eg: SAEC, ROI, ...)
% dataWriter: Sotware that write data
% writerVersion: Unique version of writer (eg: Git SHA1, see h5RoiGen)
% examDate: yyyy/MM/dd HH:mm:ss
% patientName: Exam Id
% serieNumber: Serie Number
    data.attributes = {};
    data.attributes.DATA_TYPE = dataType;
    data.attributes.DATA_WRITER = dataWriter;
    data.attributes.PLUGIN_SHA1 = writerVersion;
    data.attributes.examDate = examDate;
    data.attributes.patientName = patientName;
    data.attributes.serieNumber = serieNumber;
end