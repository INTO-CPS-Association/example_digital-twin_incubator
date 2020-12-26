# Start influxdb server

To start the influxdb server, run:
1. Make sure docker is configured to share the database folder [influxdb](./influxdb).
   See the [manual](https://docs.docker.com/docker-for-windows/).
2. Start influxdb: `docker-compose up --detach --build`
3. Run script to test db connection
   ```
   cd [RepoRoot]\software
   [Activate virtual environment]
   python -m digital_twin.data_access.influxdbserver.test_server
   ```
4. Stop and remove the server: `docker-compose down -v`

More information: https://docs.influxdata.com/influxdb/v2.0/get-started/

# Management of rabbitmq

1. Start influxdb server
2. Open http://localhost:8086/ on your browser.
3. Alternative, open a terminal in the container: `docker exec -it influxdb-server /bin/bash`

# Initial Setup of Database

This has been done once, and there's no need to repeat it.

1. Open http://localhost:8086/
2. Press Get-Started
3. Enter information:
    ```
    user: incubator
    pass: incubator
    organization: incubator
    bucket: incubator 
    ```


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
