function data = h5RoiSave(filename, data)
    data.ROI.values = uint64(zeros(size(data.ROI.values));
    
    i = 1;
    for nPow = data.ROI.attributes.pows'
        tmp = bitshift(uint64(data.ROI.rois{i}), nPow);
        data.ROI.values = bitor(data.ROI.values, tmp);
        
        i = i + 1;
    end

    h5save(filename, data);
end  
    
