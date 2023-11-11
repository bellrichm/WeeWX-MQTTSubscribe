#! /bin/bash
#
#    Copyright (c) 2023 Rich Bell <bellrichm@gmail.com>
#
#    See the file LICENSE.txt for your full rights.
#
source ./devtools/python_versions.sh

for version in ${weewx4_python_versions[@]}; do
    ./devtools/lint.sh weewx4 $version
done
for version in ${weewx5_python_versions[@]}; do
    ./devtools/lint.sh weewx5 $version
done