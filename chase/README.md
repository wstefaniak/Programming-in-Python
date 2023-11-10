# How to create, install and run 'chase'.

### How to create 'chase' package:
To create the package run following command in [chase directory](C:\Users\wojte\Desktop\Studia\VSEM\PiP):
`python setup.py sdist`
This will create a 'dist' directory containing a source distribution of the chase package.

### How to install 'chase' package:
You can then install the package in a virtual environment using the following command in [chase directory](C:\Users\wojte\Desktop\Studia\VSEM\PiP):
`pip install dist/chase-0.1.tar.gz`

### How to run 'chase' simulation:
To run the simulation you can either run `chase [ARG]` or `python -m chase [ARG]` command, where ARG are the optional arguments of a simulation.
To see the list of all possible arguments run one of the above commands with `-h` or `--help` argument.