Welcome to the documentation of hydrograph-py
================================================

Hydrograph-py is a hydrological Python package that provides some tools for:

  1. Separation of flow time-series into peak flow and baseflow.
  2. Filtering of peak flow events given a minimum event duration.
  3. Calculation of peak event volumes.
  4. Calculation of maximum annual peak flow and maximum annual peak event volume.
  5. Extreme value analysis using GEV fitting and plotting functions.
  
Streamflow separation in this package is based on the principle introduced by :cite:`Hewlett1967`. They separated the hydrograph into 
"quickflow" and "delayed flow" components by arbitrarily projecting a line of constant slope from the beginning of any stream rise until
it intersected the falling side of the hydrograph. 

Contents
========

.. toctree::
   :maxdepth: 2
   
   installation
   
   functions
   
   references
   
   
Copyright
=========   
Copyright (C) 2019 Wilco Terink. Hydrograph-py is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`__.
