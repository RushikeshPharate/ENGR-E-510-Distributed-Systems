# DistributedKey-Value Store

```
RushikeshPharate
```
## Overview

Consistency model defines the validsequenceofoperations inagiven distributedsystem.
Thereisawiderangeofconsistencymodelsavailabletoday.Themainonesthatwearegoing
toimplementare
1) Linearizability
2) Sequentialconsistency
3) Eventualconsistency
4) Causalconsistency

Algorithm/controlflowforeachconsistencylevel

**1. Linearizability:**
    ● TheclientissuesGET/SETrequesttoanyoftheservers.
    ● Afterreceivingtheclientrequest,theserver,ifnotprimary
       ○ Creates a new thread and makes an RPC call to primary and sends the
          GET/SETrequestdetails
       ○ Maintainsaconnectiontotheclient **(Blockingrequest)**
       ○ Waitsforamessagefromtheprimary
    ● Uponreceivingthemessagefromanyserver,theprimaryserver
       ○ Maintainsaqueueforincomingrequestsusinglock
       ○ Acquireslock,andbroadcasts(ACTION,VARIABLE,VALUE)message
       ○ Whenallthemessagesreturn,releasesthelock
    ● Afterreceivingthebroadcastmessage,theserver
       ○ Updatesitslocalstorewiththereceivedvariabledetails,ifitsaSETrequest
       ○ IfitsaGETrequestsdoesn’tdoanything
       ○ Iftherequestingserver,thenitreadsthevalueofthevariableandsendsitback
          toclientviathemaintainedconnectionandclosestheclientconnection
**2. SequentialConsistency:**
    ● TheclientissuesGET/SETrequesttoanyoftheservers.
    ● Afterreceivingtheclientrequest,theserver,ifnotprimary
       ○ IfitsaSETrequest
          ■ CreatesanewthreadandmakesanRPCcalltoprimary
          ■ SendstheSETrequestdetails
          ■ Maintainsaconnectiontotheclient( **Blockingrequest** )


```
○ IfitsaGETrequest
■ Readsthevalueofthevariablefromthelocalstore.
■ Returnthevalueimmediatelyifthevariableispresentinthestoreelse
returnNone.
■ Closetheclientconnection( Non-Blockingrequest )
● Uponreceivingthemessagefromanyserver,theprimaryserver
○ Maintainsaqueueforincomingrequestsusinglock
○ Acquireslock,andbroadcasts(ACTION,VARIABLE,VALUE)message.(Note:
ACTIONisalwaysSET insequentialconsistency becauseweonlybroadcast
SETrequests)
○ Whenallthemessagesreturn,releasesthelock
● Afterreceivingthebroadcastmessage,theserver
○ Updatesitslocalstorewiththereceivedvariabledetails.
○ Iftherequestingserver,thenitclosestheclientconnection
```
**3. EventualConsistency:**
    ● TheclientissuesGET/SETrequesttoanyoftheservers.
    ● Afterreceivingtheclientrequest,theserver,ifnotprimary
       ○ IfitsaSETrequest
          ■ CreatesanewthreadandmakesanRPCcalltoprimaryandsendsthe
             SETrequestdetails
          ■ Inthe mainthread, closesthe connectionto theclient( **Non-Blocking**
             **request** )
       ○ IfitsaGETrequest
          ■ Readsthevalueofthevariablefromthelocalstore.
          ■ Returnthevalueimmediatelyifthevariableispresentinthestoreelse
             returnNone.
          ■ Closetheclientconnection( **Non-Blockingrequest** )
    ● Uponreceivingthemessagefromanyserver,theprimaryserver
       ○ Maintainsaqueueforincomingrequestsusinglock
       ○ Acquireslock,andbroadcasts(ACTION,VARIABLE,VALUE)message.(Note:
          ACTIONisalwaysSETineventualconsistencybecauseweonlybroadcastSET
          requests)
       ○ Whenallthemessagesreturn,releasesthelock
    ● Afterreceivingthebroadcastmessage,theserver
       a. Updatesitslocalstorewiththereceivedvariabledetails.
       b. Doesnotcareabouttheclientconnectionasitsalreadyclosed.


**4. CausalConsistency:**

```
● Everyclientmaintains alogical clockmaintainingthe version ofeachvariablethatit
dealswith
● Similarlyeachserveralsokeepstrackofeachvariablelogicalclock
● Everyrequestfrom clientcontainsaminimumacceptable logicalclockvalueforthat
variablealongwiththeGET/SETrequestdetails
● EveryresponsefromservercontainstheUpdated/Latestlogicalvalueforthatvariable
alongwiththeGET/SETresponse
```
Now,thealgorithm:

```
● TheclientissuesGET/SETrequesttoanyoftheserversalogwithminimumacceptable
logicalclockvalue.
● Afterreceivingtheclientrequest,theserver,ifnotprimary
○ IfitsaSETrequest
■ CreatesanewthreadandmakesanRPCcalltoprimaryandsendsthe
SETrequestdetails
■ In the mainthread, waits to get an updateon thelogical clockfrom
primary
■ Whentheservergetsamessagefromprimary,itupdatesitlogicalclock
value, local store and sends the latest clock value tothe clientasa
responseandclosestheconnection.
○ IfitsaGETrequest
■ Compares the request logical clock with itsownlogical clockforthat
variable
■ Iftherequestslogicalclockvalueisgreaterthanitsownthenitessentially
meansthatthismessageisfromthefutureanditneedstowaitforsome
timetorespondtothis.
■ Inthemeantime,ifit receivestheupdateviabroadcastformprimary,it
updatesitslogicalclock.Assoonasitslogicalclockbecomesequaltoor
greaterthantheclientrequestslogicalclock,itreadsthevalueforthat
variable fromthe localstoreand returnsit to theclientalongwiththe
latestlogicalclockvalueforthatvariable
■ Closestheconnectiontoclient
● Uponreceivingthemessagefromanyserver,theprimaryserver
○ Maintainsaqueueforincomingrequestsusinglock
○ Acquireslock,incrementslogical clockfortheVARandbroadcasts(ACTION,
VARIABLE, VALUE) message. (Note: ACTION is always SET in causal
consistencybecauseweonlybroadcastSETrequests)
○ Whenallthemessagesreturn,releasesthelock
```

```
● Afterreceivingthebroadcastmessage,otherservers
a. Updatestheirlocalstorewiththereceivedvariabledetails.
b. Updatesthelogicalcounterforthatvariable.
```
PleaserefertothebelowtableforacomparisonofthenatureofGET/SETrequestsforeach
consistencymodel

```
Consistency
Model
```
```
Linearizability Sequential Eventual Causal
```
```
SETrequest Blocking Blocking Non-Blocking Somewhat
Non-Blocking
```
```
GETrequest Blocking Non-Blocking Non-Blocking Somewhat
Non-Blocking
TableBlocking/non-Blocking
```

## StepstoRunDistributedKey-ValueStore:

### ● Prerequisites

- Youhavethesubmissionfolder
- YourbasedirectoryistheDist-KV-Storefolder

### ● StartingtheServers:

- Open _config.json_ fileand change _NO_OF_SERVERS, PORT_START_RANGE_ ,or
    anyotherparameterasperyourconvenience.
- Openanewterminalandrun **_python 3 main.py_** command
- After this logs will be generated informing you about the servers and their
    accessibilityonports.

### ● StartingtheClient:

- _client.py_ filecontainsacodetomakea _GET/SET_ requesttoanyserver.
- Thereare 2 waystorunanclient:
    - Run **_python 3 client.py[serveraddress][serverportnumber] [command]_**
       **_[var][value]_** command.Here,commandcanbeeitherGET/SET. _[Value]_ should
       onlybepassedforSETrequests.
          1. ex.SETrequest→ _python3client.pylocalhost 6486 SETx 5_
          _2._ exGETrequest→ _python3client.pylocalhost 6486 GETx_
    - Run _bash run_clients.py_ command after making commenting/uncommenting
       requireddetailsinthe _run_clients.py_ file.Thiswillinturncalltheabovecommand
       butyoucanchangethisshellfiletomakeconcurrentrequeststothesameor
       differentservers.
- Runningclientforcausalconsistencyisabitdifferentasweneedtocontactmultiple
    servers.Makesure _NO_OF_SERVERS_ isset 10 in _config.json_ fileastheportsare
    hardcodedforcausalclient.
    - Run _python3 client_causal.py localhost_ or navigateto _test-cases/[consistency_
       _model]_ andrun _bashrun_clients.py_

```
● Whenaclientisstarted,thelogswillbegeneratedintheserverterminalandyoucan
seethelogicflow
```
### ● RunTestCases:

- Thesubmission folderhasa _testcases_ folderwhichcontainsbashscriptsfor
    testingdifferentconsistencylevels
- Navigateto _testcases/[consistencymodel]_ folder
- Run _bashrun_clients.sh_ command
- Thisshouldstartatestcaseforaparticularconsistencymodel.Youcanalways
    changetheshellscriptbasedonwhatyouwishtotest.
- Bashscriptsforperformancetestingarealsothereintherespectivefolders.


## PerformanceEvaluation:

```
ConsistencyModel Linearizability
(milliseconds)
```
```
Sequential
(milliseconds)
```
```
Eventual
(milliseconds)
```
```
Causal
(milliseconds)
```
```
SET request (avg of
100 requests and 10
servers)
```
#### 278.77 288.72 63.96 234.

```
GET request(avg of
100 requests and 10
servers)
```
#### 158.36 62.62 63.42 66.

PleaseNote:Forcausalconsistency,theGETrequestsareconditionallyblockingsoideallythe
latencyshouldbehigherthan66.01milliseconds.AsIwasnotabletocreateancircumstance
for 100 requeststowait,thisisjustnormalNon-BlockingGETrequest

```
Fig
```

Asyoucanclearlyseefromthegraph,overallEventualconsistencymodelisthefastest.The
secondfastestistheCausalandafterthatcomesSequentialmodel.Theslowestamongst 4 is
theLinearizability.

## Challenges:

- Themostchallengingpartoftheassignmentoftestingthebehaviorofeachconsistency
    modelandmakingsureitscorrect.Iusedloggingforthisandhaveusedcustomdelays
    insomeplacestodemonstrateinthetestcases.
- Anotherchallengingpartwasdevelopingtheprimary-basedbroadcastalgorithm.Ihad
    usedasimilaralgorithmforDistributedSequenceralgorithmsothathelped.
- CausalconsistencyImplementationasthealgorithmprovidedintheslidesisnotclear.

## LimitationsandFutureImprovement

```
1) Current algorithm is very centered around primary and thiswill createperformance
issuesandprimaryisdoingmostoftheheavylifting.Toovercomethiswecanusea
total-order multicast algorithm that will solvetheperformanceissuebut hasitsown
complexityissues.
2) Ifoneoftheserverfails,thewholesystemmightcrash.Thiscanbeavoidedifweuse
somekindoffaulttolerance.
```

## TestCases:

## Linearizability:

**Servers 1 to 3 arerunningon 6485 to 6487 portsrespectively**

**Sequenceofrequest:**

```
1) SETx 7 onserver 2
2) SETx 1 onserver 2
3) GETx onserver 3 & SETx 3 onserver 2 →simultaneousrequests
```
**ServerLogs:**

PleaseChooseConsistencyLevel
**1.Linearizability**
2.SequentialConsistency
3.CausalConsistency
4.EventualConsistency
**1**
[2023-04-2623:47:30.863][INFO]ControllerNodestartedonlocalhost:
[2023-04-2623:47:30.863][INFO]Starting 3 servers
[2023-04-2623:47:32.959][INFO]Server 1 istheprimaryserver
[2023-04-2623:47:32.970][INFO]Primaryservergotdetailsofallotherservers
[2023-04-26 23:47:34.965] [INFO ] SERVER 3 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-26 23:47:34.968] [INFO ] SERVER 2 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-26 23:47:34.975] [INFO ] SERVER 1 CAN HANDLE CLIENT REQUESTS ON
localhost:


[2023-04-2623:47:36.967][INFO]Server 3 isREADY
[2023-04-2623:47:36.970][INFO]Server 2 isREADY
[2023-04-2623:47:36.977][INFO]PrimaryServercreatedanconnectiontoserver 2
[2023-04-2623:47:36.979][INFO]PrimaryServercreatedanconnectiontoserver 3
[2023-04-2623:47:36.979][INFO]Server 1 isREADY
**[2023-04-2623:47:38.302][INFO]Server 2 receivedSET(x,7)request**
[2023-04-2623:47:38.304][INFO]PrimaryserverreceivedanSET(x,7)messagefromserver 2
[2023-04-2623:47:38.320][INFO]PrimaryserverstartinganbroadcastforSET(x,7)
[2023-04-2623:47:38.337][INFO]SET(x,7)finishedonserver 1
[2023-04-2623:47:38.360][INFO]SET(x,7)finishedonserver 3
[2023-04-2623:47:38.372][INFO]SET(x,7)finishedonserver 2
[2023-04-2623:47:38.503][INFO]SET(x,7)Blockingoperationendsonserver 2
**[2023-04-2623:47:39.565][INFO]Server 2 receivedSET(x,1)request**
[2023-04-2623:47:39.566][INFO]PrimaryserverreceivedanSET(x,1)messagefromserver 2
[2023-04-2623:47:39.575][INFO]PrimaryserverstartinganbroadcastforSET(x,1)
[2023-04-2623:47:39.588][INFO]SET(x,1)finishedonserver 1
[2023-04-2623:47:39.603][INFO]SET(x,1)finishedonserver 3
[2023-04-2623:47:39.634][INFO]SET(x,1)finishedonserver 2
[2023-04-2623:47:39.766][INFO]SET(x,1)Blockingoperationendsonserver 2
**[2023-04-2623:47:39.825][INFO]Server 2 receivedSET(x,3)request
[2023-04-2623:47:39.826][INFO]Server 3 receivedGET(x)request**
[2023-04-2623:47:39.826][INFO]PrimaryserverreceivedanSET(x,3)messagefromserver 2
[2023-04-2623:47:39.834][INFO]PrimaryserverreceivedanGET(x,)messagefromserver 3
[2023-04-2623:47:40.635][INFO]PrimaryserverstartinganbroadcastforSET(x,3)
[2023-04-2623:47:40.650][INFO]SET(x,3)finishedonserver 1
[2023-04-2623:47:40.661][INFO]SET(x,3)finishedonserver 3
[2023-04-2623:47:40.675][INFO]SET(x,3)finishedonserver 2
**[2023-04-2623:47:40.827][INFO]SET(x,3)Blockingoperationendsonserver 2**
[2023-04-2623:47:41.676][INFO]PrimaryserverstartinganbroadcastforGET(x,)
[2023-04-2623:47:41.677][INFO]GET(x,)finishedonserver 1
[2023-04-2623:47:41.684][INFO]GET(x,)finishedonserver 2
[2023-04-2623:47:41.696][INFO]GET(x,)finishedonserver 3
**[2023-04-2623:47:41.835][INFO]GET(x)= 3 Blockingoperationendsonserver 3**

**Notethesequenceofoperationsforsimultaneousrequestsissameonalltheservers
First** **_SETx 3_** **isbroadcastedtoallthe 3 serversandthen** **_GETx_** **isbroadcasted.**


**Logs Screenshot:**

## SequentialConsistency:

**Servers 1 to 3 arerunningon 6485 to 6487 portsrespectively**

**Sequenceofrequest:**

```
1) SETx 7 onserver 2
2) GETx onserver 3 & SETx 3 onserver 2 & SETr 5 onserver 3 →Concurrentrequests
```

**Logs:**

rpharate@silo:~/ENGR-E-510-Distributed-Systems/Dist-KV-Store$python3main.py
PleaseChooseConsistencyLevel
1.Linearizability
**2.SequentialConsistency**
3.CausalConsistency
4.EventualConsistency
**2**
[2023-04-2700:33:53.442][INFO]ControllerNodestartedonlocalhost:
[2023-04-2700:33:53.442][INFO]Starting 3 servers
[2023-04-2700:33:55.536][INFO]Server 1 istheprimaryserver
[2023-04-2700:33:55.539][INFO]Primaryservergotdetailsofallotherservers
[2023-04-27 00:33:57.527] [INFO ] SERVER 2 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-27 00:33:57.533] [INFO ] SERVER 3 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-27 00:33:57.546] [INFO ] SERVER 1 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-2700:33:59.529][INFO]Server 2 isREADY
[2023-04-2700:33:59.534][INFO]Server 3 isREADY
[2023-04-2700:33:59.547][INFO]PrimaryServercreatedanconnectiontoserver 2
[2023-04-2700:33:59.547][INFO]PrimaryServercreatedanconnectiontoserver 3
[2023-04-2700:33:59.547][INFO]Server 1 isREADY
**[2023-04-2700:34:02.339][INFO]Server 2 receivedSET(x,7)request**
[2023-04-2700:34:02.342][INFO]PrimaryserverreceivedanSET(x,7)messagefromserver 2
[2023-04-2700:34:02.347][INFO]PrimaryserverstartinganbroadcastforSET(x,7)
[2023-04-2700:34:02.368][INFO]SET(x,7)finishedonserver 1
[2023-04-2700:34:02.381][INFO]SET(x,7)finishedonserver 3
[2023-04-2700:34:02.393][INFO]SET(x,7)finishedonserver 2
**[2023-04-2700:34:02.541][INFO]SET(x,7)Blockingoperationendsonserver 2
[2023-04-2700:34:03.601][INFO]Server 3 receivedSET(r,5)request
[2023-04-2700:34:03.602][INFO]Server 2 receivedSET(x,3)request**
[2023-04-2700:34:03.604][INFO]PrimaryserverreceivedanSET(r,5)messagefromserver 3
**[2023-04-2700:34:03.608][INFO]Server 3 receivedGET(x)request
[2023-04-2700:34:03.609][INFO]GET(x)= 7 Non-Blockingoperationendsonserver 3**
[2023-04-2700:34:03.609][INFO]PrimaryserverstartinganbroadcastforSET(r,5)
[2023-04-2700:34:03.610][INFO]PrimaryserverreceivedanSET(x,3)messagefromserver 2
[2023-04-2700:34:03.631][INFO]SET(r,5)finishedonserver 1
[2023-04-2700:34:03.644][INFO]SET(r,5)finishedonserver 2
[2023-04-2700:34:03.659][INFO]SET(r,5)finishedonserver 3
**[2023-04-2700:34:03.803][INFO]SET(r,5)Blockingoperationendsonserver 3**
[2023-04-2700:34:04.660][INFO]PrimaryserverstartinganbroadcastforSET(x,3)


[2023-04-2700:34:04.673][INFO]SET(x,3)finishedonserver 1
[2023-04-2700:34:04.687][INFO]SET(x,3)finishedonserver 3
[2023-04-2700:34:04.699][INFO]SET(x,3)finishedonserver 2
**[2023-04-2700:34:04.811][INFO]SET(x,3)Blockingoperationendsonserver 2**

**Note that** **_GET x_** **is a Non-Blocking operation and doesnot make an broadcast.Its
basicallyandlocalreadandreturnsimmediately.Intheaboveexample,** **_GETx_** **(server3),**
**_SETr 5_** **(server3)&** **_SETx 3_** **(server2)areconcurrentrequests.Eventhoughthe** **_SETx 3_**
**requestisreceivedprior(fewmilisecondsdifference)before** **_GETx_** **request,itsonserver
2 andthe broadcastforthatrequesthas notyetreceivedon server 3 andhencethe
currentvalueofxis 7 onserver3.So,** **_GETx_** **willreturnx=7immediately.**

**Logsscreenshot:**


## EventualConsistency:

**Servers 1 to 3 arerunningon 6485 to 6487 portsrespectively**

**Sequenceofrequests:**
1) **_SETx 7_** onserver 2
2) **_GETx_** onserver 3 & **_SETx 3_** onserver 2 & **_SETr 5_** onserver 3 →Concurrentrequests
3) **_GETr_** onserver 3

**Logs:**

rpharate@silo:~/ENGR-E-510-Distributed-Systems/Dist-KV-Store$python3main.py
PleaseChooseConsistencyLevel
1.Linearizability
2.SequentialConsistency
3.CausalConsistency
**4.EventualConsistency
4**
[2023-04-2713:24:13.102][INFO]ControllerNodestartedonlocalhost:
[2023-04-2713:24:13.102][INFO]Starting 3 servers
[2023-04-2713:24:15.191][INFO]Server 1 istheprimaryserver
[2023-04-2713:24:15.194][INFO]Primaryservergotdetailsofallotherservers
[2023-04-27 13:24:17.182] [INFO ] SERVER 3 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-27 13:24:17.187] [INFO ] SERVER 2 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-27 13:24:17.200] [INFO ] SERVER 1 CAN HANDLE CLIENT REQUESTS ON
localhost:
[2023-04-2713:24:19.183][INFO]Server 3 isREADY
[2023-04-2713:24:19.189][INFO]Server 2 isREADY
[2023-04-2713:24:19.202][INFO]PrimaryServercreatedanconnectiontoserver 2


[2023-04-2713:24:19.202][INFO]PrimaryServercreatedanconnectiontoserver 3
[2023-04-2713:24:19.202][INFO]Server 1 isREADY
[2023-04-2713:24:22.658][INFO]Server 2 receivedSET(x,7)request
[2023-04-2713:24:22.658][INFO]SET(x,7)Non-Blockingoperationendsonserver 2
[2023-04-2713:24:22.660][INFO]PrimaryserverreceivedanSET(x,7)messagefromserver 2
[2023-04-2713:24:22.666][INFO]PrimaryserverstartinganbroadcastforSET(x,7)
[2023-04-2713:24:22.688][INFO]SET(x,7)finishedonserver 1
[2023-04-2713:24:22.704][INFO]SET(x,7)finishedonserver 3
[2023-04-2713:24:22.722][INFO]SET(x,7)finishedonserver 2
[2023-04-2713:24:23.725][INFO]Server 3 receivedGET(x)request
[2023-04-2713:24:23.726][INFO]GET(x)= 7 Non-Blockingoperationendsonserver 3
[2023-04-2713:24:23.726][INFO]Server 2 receivedSET(x,3)request
**[2023-04-2713:24:23.726][INFO]Server 3 receivedSET(r,5)request**
[2023-04-2713:24:23.730][INFO]SET(x,3)Non-Blockingoperationendsonserver 2
**[2023-04-2713:24:23.731][INFO]SET(r,5)Non-Blockingoperationendsonserver 3**
[2023-04-2713:24:23.731][INFO]PrimaryserverreceivedanSET(x,3)messagefromserver 2
[2023-04-2713:24:23.733][INFO]PrimaryserverreceivedanSET(r,5)messagefromserver 3
[2023-04-2713:24:23.737][INFO]PrimaryserverstartinganbroadcastforSET(x,3)
[2023-04-2713:24:23.760][INFO]SET(x,3)finishedonserver 1
[2023-04-2713:24:23.775][INFO]SET(x,3)finishedonserver 3
**[2023-04-2713:24:23.792][INFO]Server 3 receivedGET(r)request**
[2023-04-2713:24:23.795][INFO]SET(x,3)finishedonserver 2
**[2023-04-2713:24:23.792][INFO]GET(r)=NoneNon-Blockingoperationendsonserver 3
[2023-04-2713:24:24.803][INFO]PrimaryserverstartinganbroadcastforSET(r,5)**
[2023-04-2713:24:24.816][INFO]SET(r,5)finishedonserver 1
[2023-04-2713:24:24.827][INFO]SET(r,5)finishedonserver 2
[2023-04-2713:24:24.839][INFO]SET(r,5)finishedonserver 3

**AsyoucanseeinthelogsbothGETand SEToperationsareNon-Blocking.GETrequest
immediately return the local value of the variable and SET requests also returns
immediately.Thebroadcastmessagecanstartsafterthe SETrequestisterminatedas
youcanseeintheselogs.**

**Server 3 receives** **_SETr 5_** **requestanditreturnimmediatelybeforethebroadcast.The
broadcast for this requests starts later. Now, when another server receives** **_GET r_**
**requestsitreturnsNoneimmediately(localread)asthatvariabledoesn’texistinanyof
theserverasthebroadcastforithasnothappened.**


**Logs screenshot:**


## CausalConsistency:

Ihaveused 10 serversforthiscase.Itwasnecessarytodemonstratethecausalconsistency
behavior.Also,Ihaveusedsomesleepstatementinordertologeventsasneededandcreatea
scenariothatwill differentiate betweencausal consistencyand sequentialconsistency.Also,
note that the client is differentthan the rest ofthe models implementationaswe need to
maintainversionvectors(logicalclocks)ontheclientsideaswell.

**Servers 1 to 10 arerunningon 6485 to 6494 portsrespectively**

**Sequenceofrequests:**
1) **_SETx[randomvalue]_** onserver 2
2) **_GETx_** onserver 3
3) **_GETx_** onserver 10

**Logs:**
rpharate@silo:~/ENGR-E-510-Distributed-Systems$cdDist-KV-Store/
rpharate@silo:~/ENGR-E-510-Distributed-Systems/Dist-KV-Store$python3main.py
PleaseChooseConsistencyLevel
1.Linearizability
2.SequentialConsistency
**3.CausalConsistency**
4.EventualConsistency
**3**
[2023-04-2922:55:56.731][INFO]ControllerNodestartedonlocalhost:


[2023-04-2922:55:56.731][INFO]Starting 10 servers
[2023-04-2922:55:58.889][INFO]Server 1 istheprimaryserver
[2023-04-2922:55:58.915][INFO]Primaryservergotdetailsofallotherservers
[2023-04-2922:56:00.858][INFO]SERVER 2 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.871][INFO]SERVER 3 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.879][INFO]SERVER 5 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.886][INFO]SERVER 6 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.895][INFO]SERVER 8 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.900][INFO]SERVER 10 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.903][INFO]SERVER 4 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.910][INFO]SERVER 9 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.919][INFO]SERVER 1 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:00.913][INFO]SERVER 7 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-04-2922:56:02.859][INFO]Server 2 isREADY
[2023-04-2922:56:02.871][INFO]Server 3 isREADY
[2023-04-2922:56:02.881][INFO]Server 5 isREADY
[2023-04-2922:56:02.887][INFO]Server 6 isREADY
[2023-04-2922:56:02.897][INFO]Server 8 isREADY
[2023-04-2922:56:02.902][INFO]Server 10 isREADY
[2023-04-2922:56:02.904][INFO]Server 4 isREADY
[2023-04-2922:56:02.912][INFO]Server 9 isREADY
[2023-04-2922:56:02.915][INFO]Server 7 isREADY
[2023-04-2922:56:02.921][INFO]PrimaryServercreatedanconnectiontoserver 2
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 3
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 4
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 5
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 6
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 7
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 8
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 9
[2023-04-2922:56:02.922][INFO]PrimaryServercreatedanconnectiontoserver 10
[2023-04-2922:56:02.922][INFO]Server 1 isREADY
**[2023-04-2922:56:46.599][INFO]Server 2 receivedSET(x,51)requestwithlogicalclockvalue 0**
[2023-04-2922:56:46.599][INFO]Currentlogicalclockvalueforvariablexonserver 2 is 0
[2023-04-2922:56:46.602][INFO]PrimaryserverreceivedanSET(x,51)messagefromserver 2
[2023-04-2922:56:46.617][INFO]PrimaryserverstartinganbroadcastforSET(x,51)
[2023-04-2922:56:46.674][INFO]SET(x,51)finishedonserver 1
[2023-04-2922:56:46.674][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 1
[2023-04-2922:56:47.689][INFO]SET(x,51)finishedonserver 2
[2023-04-2922:56:47.689][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 2
[2023-04-2922:56:48.738][INFO]SET(x,51)finishedonserver 3
[2023-04-2922:56:48.738][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 3
**[2023-04-2922:56:48.802][INFO]SET(x,51)operationendsonserver 2 withlogicalclockvalue 1
[2023-04-2922:56:48.804][INFO]Server 3 receivedGET(x)requestwithlogicalclockvalue 1
[2023-04-2922:56:48.808][INFO]Currentlogicalclockvalueforvariablexonserver 3 is 1
[2023-04-2922:56:48.808][INFO]GET(x)= 51 operationendsonserver 3 withlogicalclockvalue 1
[2023-04-2922:56:48.818][INFO]Server 10 receivedGET(x)requestwithlogicalclockvalue 1
[2023-04-2922:56:48.825][INFO]Currentlogicalclockvalueforvariablexonserver 10 is 0**


**[2023-04-2922:56:48.825][INFO ]Waitingforserver10'slogicalclock: 0 tocatchuptoclients
logicalclock: 1 forvariablex
[2023-04-2922:56:48.825][INFO]BlockingexecutionofGET(x)request**
[2023-04-2922:56:49.752][INFO]SET(x,51)finishedonserver 4
[2023-04-2922:56:49.752][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 4
[2023-04-2922:56:50.765][INFO]SET(x,51)finishedonserver 5
[2023-04-2922:56:50.765][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 5
[2023-04-2922:56:51.788][INFO]SET(x,51)finishedonserver 6
[2023-04-2922:56:51.788][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 6
[2023-04-2922:56:52.802][INFO]SET(x,51)finishedonserver 7
[2023-04-2922:56:52.802][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 7
[2023-04-2922:56:53.814][INFO]SET(x,51)finishedonserver 8
[2023-04-2922:56:53.814][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 8
[2023-04-2922:56:54.828][INFO]SET(x,51)finishedonserver 9
[2023-04-2922:56:54.828][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 9
[2023-04-2922:56:55.841][INFO]SET(x,51)finishedonserver 10
[2023-04-2922:56:55.841][INFO]Updatedlogicalclockvaluefrom 0 to 1 forvariablexonserver 10
[2023-04-2922:56:56.033][INFO] **Finallycatchedup.....Server10'slogicalclock:1,Getrequests
logicalclock: 1 forvariablex
[2023-04-2922:56:56.033][INFO]GET(x)= 51 operationendsonserver 10 withlogicalclockvalue
1**

**Asyoucanseeinthelogs,first,server 2 receivesSET(x,51)request.**

**- Servers2’slogicalclockis 0 atthismoment.
- Server 2 forwardsthiswriterequesttoprimary
- Primaryserverincrementsthelogicalclockforthisvariableandsendsthistoserver 2
- Server 2 updatesitscounterforvariablexandthenreturnsthisvaluetoclient.
- Primaryserverbroadcaststhisupdatealongwiththisnewlogicalclockvaluetoallother**
    **servers.
- Uponreceivingtheupdatedlogicalclockvaluefromserver 2 clientsupdatesitsclockfor**
    **variablex
Now,wesendanGET(x)requesttoserver 3 alongwithlogicalclockof 1 (updatedfromservers
responsetoSETrequest)
- Server 3 hasalreadyreceivedthebroadcastmessageandhenceitimmediatelyreturnthe
valueofxwhichis 51
Now,wesendthenextGET(x)requesttoserver 10 alongwiththeupdatedlogicalclockvalue.
- WhenthisGETrequestcomestoserver10,itdoesnotprocessitandwaitsasitsown
logicalclockforvariablexisat0.
- TheGETrequestcomeswithlogicalclockof 1 whichisfromfuture.
- Thelogicalclockof server 10 isat 0 becausethebroadcastforSET(x,51)hasnotyet
reached.
- Whenserver 10 receivesthisbroadcastmessageitupdatesitslogicalclockforvariablex
to 1 andnowcanprocesstheGET(x)request.
As,youcanseeinthelogs,thisBlockingbehaviorishighlightedinyellow.**


Logs screenshot:

**Comparisonwithsequentialconsistency:**

- Insequentialconsistency,thewriteoperationsarecompletelyblockingmeaningitwill
    notreturnuntilalltheservershavethesamecopyofthevariable.
- So, in this case, the partial broadcast condition will never occur where causal
    consistencyiseffective.


Sequenceofoperation:

```
4) SETx 51 onserver 2
5) GETx onserver 3
6) GETx onserver 10
```
Logs:
rpharate@silo:~/ENGR-E-510-Distributed-Systems$cdDist-KV-Store/
rpharate@silo:~/ENGR-E-510-Distributed-Systems/Dist-KV-Store$python3main.py
PleaseChooseConsistencyLevel
1.Linearizability
**2.SequentialConsistency**
3.CausalConsistency
4.EventualConsistency
**2**
[2023-05-0212:06:29.993][INFO]ControllerNodestartedonlocalhost:
[2023-05-0212:06:29.993][INFO]Starting 10 servers
[2023-05-0212:06:32.085][INFO]Server 1 istheprimaryserver
[2023-05-0212:06:32.121][INFO]Primaryservergotdetailsofallotherservers
[2023-05-0212:06:34.074][INFO]SERVER 7 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-05-0212:06:34.095][INFO]SERVER 8 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-05-0212:06:34.103][INFO]SERVER 9 CANHANDLECLIENTREQUESTSONlocalhost:
[2023-05-0212:06:34.107][INFO]SERVER 3 CANHANDLECLIENTREQUESTSONlocalhost:


[2023-05-0212:06:34.110][INFO]SERVER 6 CANHANDLECLIENTREQUESTSONlocalhost:6490
[2023-05-0212:06:34.112][INFO]SERVER 10 CANHANDLECLIENTREQUESTSONlocalhost:6494
[2023-05-0212:06:34.119][INFO]SERVER 5 CANHANDLECLIENTREQUESTSONlocalhost:6489
[2023-05-0212:06:34.130][INFO]SERVER 4 CANHANDLECLIENTREQUESTSONlocalhost:6488
[2023-05-0212:06:34.133][INFO]SERVER 1 CANHANDLECLIENTREQUESTSONlocalhost:6485
[2023-05-0212:06:34.133][INFO]SERVER 2 CANHANDLECLIENTREQUESTSONlocalhost:6486
[2023-05-0212:06:36.076][INFO]Server 7 isREADY
[2023-05-0212:06:36.097][INFO]Server 8 isREADY
[2023-05-0212:06:36.105][INFO]Server 9 isREADY
[2023-05-0212:06:36.110][INFO]Server 3 isREADY
[2023-05-0212:06:36.111][INFO]Server 6 isREADY
[2023-05-0212:06:36.115][INFO]Server 10 isREADY
[2023-05-0212:06:36.121][INFO]Server 5 isREADY
[2023-05-0212:06:36.131][INFO]Server 4 isREADY
[2023-05-0212:06:36.135][INFO]PrimaryServercreatedanconnectiontoserver 2
[2023-05-0212:06:36.136][INFO]Server 2 isREADY
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 3
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 4
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 5
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 6
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 7
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 8
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 9
[2023-05-0212:06:36.141][INFO]PrimaryServercreatedanconnectiontoserver 10
[2023-05-0212:06:36.141][INFO]Server 1 isREADY
**[2023-05-0212:10:12.304][INFO]Server 2 receivedSET(x,51)request**
[2023-05-0212:10:12.307][INFO]PrimaryserverreceivedanSET(x,51)messagefromserver 2
[2023-05-0212:10:12.313][INFO]PrimaryserverstartinganbroadcastforSET(x,51)
[2023-05-0212:10:12.326][INFO]SET(x,51)finishedonserver 1
[2023-05-0212:10:12.340][INFO]SET(x,51)finishedonserver 3
[2023-05-0212:10:12.354][INFO]SET(x,51)finishedonserver 4
[2023-05-0212:10:12.369][INFO]SET(x,51)finishedonserver 5
[2023-05-0212:10:12.382][INFO]SET(x,51)finishedonserver 6
[2023-05-0212:10:12.401][INFO]SET(x,51)finishedonserver 7
[2023-05-0212:10:12.419][INFO]SET(x,51)finishedonserver 8
[2023-05-0212:10:12.437][INFO]SET(x,51)finishedonserver 9
[2023-05-0212:10:12.456][INFO]SET(x,51)finishedonserver 10
[2023-05-0212:10:12.474][INFO]SET(x,51)finishedonserver 2
**[2023-05-0212:10:12.505][INFO]SET(x,51)Blockingoperationendsonserver 2
[2023-05-0212:10:12.507][INFO]Server 3 receivedGET(x)request
[2023-05-0212:10:12.513][INFO]GET(x)= 51 Non-Blockingoperationendsonserver 3
[2023-05-0212:10:12.521][INFO]Server 10 receivedGET(x)request
[2023-05-0212:10:12.527][INFO]GET(x)= 51 Non-Blockingoperationendsonserver 10**

**Asyoucanseehereinlogs,thefirst** **_SETx 51_** **requestisaBlockingrequestincaseofa
sequentialconsistenctstoreandhencedoesn’treturnuntilalltheserversareupdatedto
x=51andtherequestsfromthesameclientwillgetthesameresult.Inthiscase,boththe**
**_GETx_** **requestsaftertheSETgotthecorrectx=51result.**


**Incaseofthe causalconsistentstore,thisisnotthecase.Thewriteisanon-blocking
operationandimmediatelyreturns.Thismeanswritesarefastcomparedtosequential.
But,nowitcanhappenthatthesameclientmaygetdifferentresponsesforGETrequests
basedontheservercontacted.Acausalconsistentstoredoesn’tallowthattohappen
usingversions(clocks)asshownintheinitialtestcase.**

Logsscreenshot:


