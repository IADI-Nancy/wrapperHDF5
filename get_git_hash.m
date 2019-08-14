function hash = get_git_hash( filename )
%get_git_hash Performs a system call to `git rev-parse` and return the hash value.
    [filepath,name,ext] = fileparts(filename);
    command = [ 'git --git-dir ' filepath '/.git rev-parse HEAD'];
    [status,hash] = system(command);
    if( status ~= 0 )
        error('Unable to get hash from file.');
    end
end