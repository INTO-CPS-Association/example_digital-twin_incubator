# First time configuration of influxdb server

Run the following if this is the first time you're starting the influxdb server:
1. Unzip [influxdb.zip](./influxdb.zip) into a new directory called [influxdb](./influxdb).
   The directory tree should look like: 
   ```powershell
   │   config.yaml
   │   docker-compose.yml
   │   Dockerfile
   │   influxdb.zip
   │   README.md
   │   test_server.py
   └───influxdb
       │   influxd.bolt
       │
       └───engine
           └───data
   ```
2. Make sure docker is configured to share the database folder [influxdb](./influxdb).
   See the [manual](https://docs.docker.com/docker-for-windows/).
   
   Tips: Icon of the Docker-> right click-> settings-> resource -> File sharing-> "Add the influxdb folder you just unzipped."
3. Start the influxdb server (see instructions below).

# Start influxdb server

To start the influxdb server, run:
1. Start influxdb: `docker-compose up --detach --build`
2. Run script to test db connection
   ```
   cd [RepoRoot]\software
   [Activate virtual environment]
   python -m digital_twin.data_access.influxdbserver.test_server
   ```
3. See the data produced by the script by logging in to http://localhost:8086/ and opening the test dashboard.
3. Stop and remove the server: `docker-compose down -v`

More information: https://docs.influxdata.com/influxdb/v2.0/get-started/

# Management of influxdb

1. Start influxdb server
2. Open http://localhost:8086/ on your browser.
3. Alternative, open a terminal in the container: `docker exec -it influxdb-server /bin/bash`

# Initial Setup of Database

This has been done once, and there's no need to repeat it.
But it is left here in case we loose the file [influxdb.zip](./influxdb.zip).

1. Open http://localhost:8086/
2. Press Get-Started
3. Enter information:
    ```
    user: incubator
    pass: incubator
    organization: incubator
    bucket: incubator 
    ```
4. Run the [test_server.py](./test_server.py) script to start pushing random data onto the db.
5. Create dashboards by importing the json files in [dashboards](./dashboards) in the management page http://localhost:8086/

# Common Errors

## Docker build error

The following error is caused because docker is not configured to allow sharing of the local folder:
```
ERROR: for dfe365cefb0c_influxdb-server  Cannot create container for service influxdb: status code not OK but 500:  ☺   ˙˙˙˙☺       ♀☻   FDocker.Core, Version=3.0.0.50646, Culture=neutral, PublicKeyToken=null♣☺   ←Docker.Core.DockerExc
WatsonBuckets☺☺♥♥☺☺☺ ☺ ☺▲System.Collections.IDictionary►System.Excepti☻☻   ♠♥   ←Docker.Core.DockerException♠♦   ▲Filesharing has been cancelledce


♠♣   Ś‼   at Docker.ApiServices.Mounting.FileSharing.<DoShareAsync>d__8.MoveNext() in C:\workspaces\PR-15077\src\github.com\docker\pinata\win\src\Docker.ApiServices\Mounting\FileSharing.cs:line 0
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at Docker.ApiServices.Mounting.FileSharing.<ShareAsync>d__6.MoveNext() in C:\workspaces\PR-15077\src\github.com\docker\pinata\win\src\Docker.ApiServices\Mounting\FileSharing.cs:line 55
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at Docker.HttpApi.Controllers.FilesharingController.<ShareDirectory>d__2.MoveNext() in C:\workspaces\PR-15077\src\github.com\docker\pinata\win\src\Docker.HttpApi\Controllers\FilesharingController.cs:line 21
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at System.Threading.Tasks.TaskHelpersExtensions.<CastToObject>d__1`1.MoveNext()
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at System.Web.Http.Controllers.ApiControllerActionInvoker.<InvokeActionAsyncCore>d__1.MoveNext()
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at System.Web.Http.Controllers.ActionFilterResult.<ExecuteAsync>d__5.MoveNext()
--- End of stack trace from previous location where exception was thrown ---
   at System.Runtime.ExceptionServices.ExceptionDispatchInfo.Throw()
   at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)
   at System.Web.Http.Dispatcher.HttpControllerDispatcher.<SendAsync>d__15.MoveNext()
    ♠♠   Ł☺8
MoveNext
```
