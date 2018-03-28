# Varsom data repository
This repository contains methods and modules for analysing data in regObs (observations) and Varsom (forecasts). Core functions can be used for accessing api's for regObs, the forecasting-api and the chartserver/gts which provides charts to seNorge and xGeo.

Both repository root- and core modules should be viewed as a work in progress. This repository is developed as the need for data is encountered.

This said, lots of this works fine and all of it gives insight in how to read the api's we have in Varsom.

**Repository content:**<br>
`allforecasteddangerlevels.py`: Requests all forecasts (danger levels and problems) from the forecast api and writes to .csv file or plot.\<br>
`avalancheactivity.py`:<br>
`avalancheproblems.py`:<br>
`elrappdata.py`:<br>
`forcastersregions.py`:<br>
`forecasterfollowup.py`:<br>
`incidentandforecast.py`:<br>
`incidentandforecastnodelist.py`:<br>
`levelanddangersign.py`:<br>
`localstorage`: Folder holding part of a calculation or data set. Eg, requesting data may take time, so a .pickle of the data set may be stored locally while working on the analysis.<br>
`locationcheck.py`:<br>
`mainmessages.py`:<br>
`matrix.py`:<br>
`observations.py`: Methods and analysis of observations as a whole. Looks mostly on when, where and who of observations over year(s).<br>
`output`: Folder for saving plots and data files made by the different modules.<br>
`plotdangerandproblem.py`: The code for downloading and making the plots on ragnar.pythonanywhere.com/dangerandproblem/<br>
`plotobserversdata.py`: The code for downloading and making the plots on ragnar.pythonanywhere.com/observerdata/<br>
`regobsstatistics.py`: Seasonal plots over data in regObs. Eg observations pr day, annual sum etc./<br>
`runonshedule.py`: Contains the code which runs the modules and makes the file transfer to ragnar.pythonanywhere.com/observerdata/<br>
`setenvironment.py`: Contains environment variables such as api versions and folder-paths.<br>

**Repository content - core files:**<br>
`fencoding.py`: Handles removing and adding of norwegian letters. In general æ, ø and å are removed from data on retrieval from the api's and added when plotted or written to file.<br>
`getaps.py`: Code testing requests to the Avalanche Problem Solver (APS).<br>
`getdangers.py`: Contains classes and methods for retrieving avalanche danger regardless source (regObs or forecastAPI or version/year the data is from.)<br>
`getfloodwarning.py`: Code testing requests to the flood warning api.<br>
`getforecastapi.py`: Contains methods for accessing data on the forecast api.<br>
`getgts.py`: Code testing requests to the grid time series application (GTS).<br>
`getkdvelements.py`: Contains methods for accessing KDV-elements used in regObs. In regObs, xKDV elements contain the link between an element ID and its name and description. This is also the contents of dropdown choices in regObs. It is useful to have a local copy of these tables.<br>
`getmisc.py`: Probably the most fun methods are here. They access different parts som the apis for small tasks. Here is a method for mapping old observations to the regions used when they were submitted and here is a method for retriving info on trips submitted.<br>
`getobservations.py`: Contains classes and methods for accessing all on the regObs OData api.<br>
`getproblems.py`: Contains classes and methods for retrieving avalanche problems regardless source (regObs or forecastAPI or version/year the data is from.)<br>
`getregobs.py`: Contains methods for accessing avalanche problems on the regObs OData api (sub module of `getproblems.py`)<br>
`getvarsompickles.py`: Contains methods for retrieving large data sets and adding them to local storage. If locally stored data exists and files are newer that a given max datetime limit, these files are used to return data. Else, new requests are made.
`input`: Configuration- or other files used in running scripts.<br>
`localstorage`: Mostly `.pickle` files. For offline work or to save time when debugging data is stored locally.<br>
`makedatabase.py`: Ive been testing how to make database tables of the observation classes. This module investigates how sqlalchemy might work for this.<br>
`makelogs.py`: Throughout the repository this module is used for creating log files.<br>
`makepickle.py`: Handles pickling and unpickling for storing data.<br>
`postobservations.py`: Code testing data posting to the regObs api.<br>
`readfile.py`: Where a read method is generic and can be utilized across modules, the method is placed here.<br>
`setcoreenvironment.py`: Contains core environment variables such as api versions and folder-paths.<br>


