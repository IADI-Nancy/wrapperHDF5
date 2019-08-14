function h5save(filename, data)
    global gspace_id
    gspace_id = H5S.create('H5S_SCALAR');
    
    if class(filename) == "string"
        filename = char(filename);
    end

    fid = H5F.create(filename);
    struct2h5(fid, data)
end

function struct2h5(node_id, data)    
    fields = fieldnames(data);
    for field = fields'
        sub = data.(field{1});
        if field{1} == "attributes"
            attributes = fieldnames(sub);
            for attribute = attributes'
                sdata = sub.(attribute{1});
                
                [space_id, type_id, sdata] = h5type(sdata);
                attr_id = H5A.create(node_id, attribute{1}, type_id, space_id, 'H5P_DEFAULT', 'H5P_DEFAULT');
                H5A.write(attr_id,type_id,sdata)
            end
        else
            if isstruct(sub)
                if isfield(sub, 'values')
                    sdata = sub.values; %permute(sub.values, fliplr(1:ndims(sub.values)));
                    
                    dcpl = H5P.create('H5P_DATASET_CREATE');
                    H5P.set_chunk(dcpl,size(sdata));
                    H5P.set_deflate(dcpl,9);
                    
                    [space_id, type_id, sdata] = h5type(sdata);
                    
                    dset_id = H5D.create(node_id, field{1}, type_id, space_id, dcpl);
                    H5D.write(dset_id, type_id, 'H5S_ALL', 'H5S_ALL', 'H5P_DEFAULT', sdata);
                    
                    if isfield(sub, 'attributes')
                        
                        attributes = fieldnames(sub.attributes);
                        for attribute = attributes'
                            sdata = sub.attributes.(attribute{1});

                            [space_id, type_id, sdata] = h5type(sdata);
                            
                            attr_id = H5A.create(dset_id, attribute{1}, type_id, space_id, 'H5P_DEFAULT', 'H5P_DEFAULT');
                            H5A.write(attr_id,type_id,sdata)
                        end
                    end
                else
                    group_id = H5G.create(node_id, field{1}, 'H5P_DEFAULT', 'H5P_DEFAULT', 'H5P_DEFAULT');
                    struct2h5(group_id, sub);
                end
            end
        end
        
    end
end

function [space_id, type_id, data_out] = h5type(data)  
    global gspace_id
    
    data_out = data;
    
    space_id = gspace_id;
    if length(data) > 1  
        if class(data) == "string" || class(data) == "char"
            data = cellstr(data);
            data_out = data;
        end
        
        if class(data) == "cell" && class(data(1)) == "char"
            H5S_UNLIMITED = H5ML.get_constant_value('H5S_UNLIMITED');
            space_id = H5S.create_simple(1,numel(data),H5S_UNLIMITED);
        else
            if class(data) ~= "char"
                data_out = permute(data, fliplr(1:ndims(data)));
                %data = data_out;
                space_id = H5S.create_simple(size(size(data), 2), size(data), []);
            end
        end
    else
        if class(data) == "string"
            data = cellstr(data);
            data_out = data;
        end
    end

    switch class(data)
       case "logical"
           type_id = H5T.copy('H5T_NATIVE_HBOOL');
       case "char"
           type_id = H5T.copy('H5T_C_S1');
           %H5T.set_size(type_id,length(data));
           H5T.set_size(type_id,'H5T_VARIABLE');
           %H5T.set_strpad(type_id,'H5T_STR_NULLTERM');
       case "cell"
           type_id = H5T.copy('H5T_C_S1');
           H5T.set_size(type_id,'H5T_VARIABLE');
       case "uint8"
           type_id = H5T.copy('H5T_NATIVE_UCHAR');
       case "uint16"
           type_id = H5T.copy('H5T_NATIVE_USHORT');
       case "uint32"
           type_id = H5T.copy('H5T_NATIVE_UINT');
       case "uint64"
           type_id = H5T.copy('H5T_NATIVE_ULONG');
       case "int8"
           type_id = H5T.copy('H5T_NATIVE_SCHAR');
       case "int16"
           type_id = H5T.copy('H5T_NATIVE_SHORT');
       case "int32"
           type_id = H5T.copy('H5T_NATIVE_INT');
       case "int64"
           type_id = H5T.copy('H5T_NATIVE_LONG');
       case "single"
           type_id = H5T.copy('H5T_NATIVE_FLOAT');
       case "double"
           type_id = H5T.copy('H5T_NATIVE_DOUBLE');
    end
end