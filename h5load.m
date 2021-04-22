function data=h5load(filename, path)
%
% data = H5LOAD(filename)
% data = H5LOAD(filename, path_in_file)
%
% Load data in a HDF5 file to a Matlab structure.
%
% Parameters
% ----------
%
% filename
%     Name of the file to load data from
% path_in_file : optional
%     Path to the part of the HDF5 file to load
%

% Author: Pauli Virtanen <pav@iki.fi>
% This script is in the Public Domain. No warranty.
% Karina 04/01/2021 version

if nargin > 1
    path_parts = regexp(path, '/', 'split');
else
    path = '';
    path_parts = [];
end

loc = H5F.open(filename, 'H5F_ACC_RDONLY', 'H5P_DEFAULT');
try
    data = load_one(loc, path_parts, path);
    H5F.close(loc);
catch exc
    H5F.close(loc);
    rethrow(exc);
end


function data=load_one(loc, path_parts, full_path)
% Load a record recursively.

while ~isempty(path_parts) && strcmp(path_parts{1}, '')
    path_parts = path_parts(2:end);
end

data = struct();

% Attributes
[status,idx_stop,cdata_out] = H5A.iterate(loc, 'H5_INDEX_CRT_ORDER', 'H5_ITER_INC', 0, @load_one_attribute, struct());
data.attributes = cdata_out;


num_objs = H5G.get_num_objs(loc);
%
% Load groups and datasets
%
for j_item=0:num_objs-1
    objtype = H5G.get_objtype_by_idx(loc, j_item);
    objname = H5G.get_objname_by_idx(loc, j_item);
    
    name = regexprep(objname, '.*/', '');
    name2 = name;
	name2(regexp(name2,'[{,}]'))=[];
	name2(regexp(name2,'[\-]'))=['_'];
    if isempty(regexp(name, '^[a-zA-Z].*', 'ONCE'))
        name2 = char('I' + name);
        
    end
    
    % KISA: length of the audio devices name is greater than 63 which is
    % max length of a variable name in MATLAB, so we have to cut it
    if contains(name2, 'AUDIO_alsa_input_usb_Burr_Brown_from_TI_USB_Audio_CODEC_00_analog_stereo')
        name2 = ['AUDIO', name2(73:end)];
    end
    
    % Group
    if objtype == 0
        if isempty(path_parts) || strcmp(path_parts{1}, name)            
            group_loc = H5G.open(loc, name);
            try
                data.(name2) = load_one(group_loc, path_parts(2:end), full_path);
                H5G.close(group_loc);
            catch exc
                H5G.close(group_loc);
                rethrow(exc);
            end
        end
      
    % Dataset
    elseif objtype == 1
        if isempty(path_parts) || strcmp(path_parts{1}, name)            
            dataset_loc = H5D.open(loc, name);
            try
                [status,idx_stop,cdata_out] = H5A.iterate(dataset_loc, 'H5_INDEX_CRT_ORDER', 'H5_ITER_INC', 0, @load_one_attribute, struct());
                data.(name2).attributes = cdata_out;
                sub_data = H5D.read(dataset_loc, ...
                    'H5ML_DEFAULT', 'H5S_ALL','H5S_ALL','H5P_DEFAULT');
                data.(name2).values = fix_data(sub_data);
                H5D.close(dataset_loc);
            catch exc
                H5D.close(dataset_loc);
                rethrow(exc);
            end
        end
    end
end

% Check that we managed to load something if path walking is in progress
if ~isempty(path_parts)
    error('Path "%s" not found in the HDF5 file', full_path);
end

function [status,data] = load_one_attribute(obj_id,attr_name,info,data)
    status = 0;
    
    attr_id = H5A.open(obj_id, attr_name);
    name2 = attr_name;
    if isempty(regexp(attr_name, '^[a-zA-Z].*', 'ONCE'))
        name2 = char('I' + attr_name);
    end
    
    try
         tmp = H5A.read(attr_id);
         if iscell(tmp)
             [w h] = size(tmp);
             if w == 1 && h == 1
                 tmp = tmp{1, 1};
             end
         end
         data.(name2) = tmp;
        H5A.close(attr_id);
    catch exc
        H5A.close(attr_id);
        rethrow(exc);
    end

function data=fix_data(data)
% Fix some common types of data to more friendly form.

if isstruct(data)
    fields = fieldnames(data);
    if length(fields) == 2 && strcmp(fields{1}, 'r') && strcmp(fields{2}, 'i')
        if isnumeric(data.r) && isnumeric(data.i)
            data = data.r + 1j*data.i;
        end
    end
end

if isnumeric(data) && ndims(data) > 1
    % permute dimensions
    data = permute(data, fliplr(1:ndims(data)));
end

if ischar(data)
    data = permute(data, fliplr(1:ndims(data)));
end
