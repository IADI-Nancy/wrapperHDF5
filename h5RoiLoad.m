function data = h5RoiLoad(filename)
    data = h5load(filename);
    
    data.ROI.rois = {};
    for nPow = data.ROI.attributes.pows'
        tmp = bitshift(uint64(ones(size(data.ROI.values))), nPow);
        data.ROI.rois{end+1} = logical(bitand(data.ROI.values, tmp));
    end
end  
    