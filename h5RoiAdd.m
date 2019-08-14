function data = h5RoiAdd(data, name, roi, operator, date, color)
% h5RoiGen generata a minimal ROI HDF5 header compatible with ArchiMed3
% data = h5RoiAdd(data, name, roi, operator, date, color)
% data : roi struct
% name: roi name
% roi: roi values (logical)
% operator : operator name (optionnal => username)
% date : roi creation date (optionnal => now)
% color : roi color (optionnal)

    if nargin<4
        operator = getenv('USERNAME');
        if operator == ""
            operator = getenv('USER');
        end
    end

    if nargin<5
        date = datestr(datetime('now'),'yyyy/mm/dd HH:MM:ss');
    end
    
    if nargin<6
        color = ['#', dec2hex(floor(rand() * 255), 2), dec2hex(floor(rand() * 255), 2), dec2hex(floor(rand() * 255), 2), '80'];
    end

    data.ROI.attributes.colors{end+1} = color;
    data.ROI.attributes.dates{end+1} = date;
    data.ROI.attributes.names{end+1} = name;
    data.ROI.attributes.operators{end+1} = operator;
    
    pows = data.ROI.attributes.pows;
    pows = sort(pows);
    ipow = 0;
    for i = 0:64
        if i >= length(pows) || i ~= pows(i + 1)
            ipow = i;
            break
        end
    end
    
    data.ROI.attributes.pows{end+1} = ipow;
    data.ROI.attributes.rois{end+1} = roi;
end