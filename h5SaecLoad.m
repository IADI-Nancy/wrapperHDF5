function data = h5SaecLoad(filename)
    data = saec3Convert(h5load(filename));
end
    
    
function data = saec3Convert(data)
    fields = fieldnames(data);
    for i = 1:numel(fields)
        if strcmp(fields{i}, 'attributes')==0 && strcmp(fields{i},'timestamp')==0
            if strcmp(fields{i},'datas')==1
                data.(fields{i}).values = double(data.(fields{i}).values) * data.attributes.channelLSBValue + data.attributes.channelOffsetValue;
            else
                data.(fields{i}) = saec3Convert(data.(fields{i}));
            end
        end
    end
end   
    