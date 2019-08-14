function data = h5RoiGen(examDate, patientName, serieNumber, roiSize, pixelSpacing)
% h5RoiGen generata a minimal ROI HDF5 header compatible with ArchiMed3
% data = h5RoiGen(examDate, patientName, serieNumber, roiSize, pixelSpacing)
% patientName: Exam Id
% serieNumber: Serie Number
% roiSize : Volume size
% pixelSpacing : Pixel Spacing
    data = h5HeaderGen('ROI', 'matlab', get_git_hash([mfilename('fullpath'), '.m']), examDate, patientName, serieNumber);
    data.attributes.pixelSpacing = pixelSpacing;
    data.ROI = {};
    data.ROI.values = uint64(zeros(roiSize));
    data.ROI.rois = {};
    data.ROI.attributes = {};
    data.ROI.attributes.colors = {};
    data.ROI.attributes.dates = {};
    data.ROI.attributes.names = {};
    data.ROI.attributes.operators = {};
    data.ROI.attributes.pows = {};
end