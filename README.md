# Varsom data repository
Repository contains methods and modules for accessing api's for regObs, The forecasting-api and The chart server which provides charts to seNorge and xGeo. All these products are a part of the Varsom-family; products used in forecasting at NVE.

**Repository content - source files:**<br>
`fencoding.py`: Handles removing and adding of norwegian letters. In general æ, ø and å are removed from data on retrieval from the api's and added when plotted or written to file.<br>
`getdangers.py`: Contains classes and methods for retrieving avalanche danger regardless source (regObs or forecastAPI or version/year the data is from.)<br>
`getforecastapi.py`: Contains methods for accessing data on the forecast api.<br>
`getkdvelements.py`: Contains methods for accessing KDV-elements used in regObs. In regObs, xKDV elements contain the link between an element ID and its name and description. This is also the contents of dropdown choices in regObs. It is useful to have a local copy of these tables.<br>
`getobservations.py`: Contains classes and methods for accessing all on the regObs OData api.<br>
`getproblems.py`: Contains classes and methods for retrieving avalanche problems regardless source (regObs or forecastAPI or version/year the data is from.)<br>
`getregobs.py`: Contains methods for accessing avalanche problems on the regObs OData api (sub module of `getproblems.py`)<br>
`makepickle.py`: Handles pickling and unpickling for storing data.<br>
`readfile.py`: Where a read method is generic and can be utilized across modules, the method is placed here.<br>
`setenvironment.py`: Contains environment variables such as api versions and folder-paths.<br>

**Repository content - "run" files:**<br>
`runallforecasteddangerlevels.py`: Saves to `Datafiles` all forecasted danger levels in all regions winter 2014/15. Includes method for saving danger levels and problems if needed.<br>
`runavalancheactivity.py`: Plots all avalanche activity compared to forecasted danger level.<br>
`runavalancheproblems.py`: Retrieves all avalanche problems (both forecasted and observed) since 2012.<br>
`runlevelanddangersign.py`: Plots all danger signs in regObs on the all forecasted danger level.
`runmainmessage.py`: Retrieves all main messages used in forecasts the winter 2014/15. Both norwegian and english. The main messages are sorted according to the danger levels and avalanche problems they appear. There is also a count of occurrences. `.csv` file is saved to `output`.<br>
`runmatrix.py`: Plots histograms of forecasted danger levels on different avalanche problems the winter 2014/15. Plots saved in `plots`.<br>
`runmplotdangerandproblem.py`: Plots forecasted and observed danger levels and a second plot comparing forecasted and observed avalanche cause for all regions.<br>

**Repository content - folders:**<br>
`input`: Configuration- or other files used in running scripts.<br>
`localstorage`: Mostly `.pickle` files. For offline work or to save time when debugging data is stored locally.<br>
`output`: All products from scripts except plots are saved to this folder.<br>
`plots`: All plot files produced are saved to tis folder.<br>
