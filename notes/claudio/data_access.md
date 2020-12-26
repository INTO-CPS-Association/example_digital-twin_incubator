Requirements for data access:
1. Needs to record incubator data
2. Needs to record other data from any components wishing to record data.
3. Needs to provide access to all of that data, from any component wishing to get it.

We have two options for the implementation of data recorder:
- A: Our own python implementation, using in memory data or CSV files.
- B: Use some timeseries database, like influx DB.

Option A is too difficult, because one has to implement requirements 2 and 3. We'd have to implement: 
- our own data model that supports flexible data insertions
- our own way to persist the data in disk (imagine dealing with csv files for this...)
- a standard protocol to record new data and access it.
Instead we can just use a database for that.

