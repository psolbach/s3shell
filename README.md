# s3shell

s3shell is a shell-like interface to Amazon Web Services s3.  
Built on top of s4cmd, it speaks a dialect of common UNIX lingo.

### Example
    $ s3shell
    
    .. welcome to s3shell
    
    > ls
    ... s3://foo
    ... s3://bar
    
    > cd <tab> s3://f <tab> s3://foo
    : xyz.com > put file.txt .
      README.md => s3://xyz.com
      
    > ls
    ...
    cat keys.json


### Installation

- touch /tmp/s3shell_completer.log
- touch /tmp/s3history.txt
- cp s3shell.py /usr/local/bin
- cd /usr/local bin
- ln -ls s3shell.py s3shell
- chmod +x s3shell
