####################
ChangeLog for Fabric
####################


Release 1.4.4 (released July 10, 2014)
--------------------------------------

* BUG#72818: BUG#18874603: THE --DAEMONIZE OPTION IN "MYSQLFABRIC MANAGE
  START" IS BROKEN
* BUG#18669231: SHARDING PRUNE ISSUE WITH 20MN RECORDS
* BUG#18904014: mysqlfabric manage setup can't find configuration file

Release 1.4.3 (released May 23, 2014)
-------------------------------------

* WL#7426: Providing performance statistics
* WL#7749: Create a clone command for cloning servers
* Bug#71701: Bug#18259479: DUMP.SHARD_* DOES NOT CONSIDER THAT A SHARD
  MAY BE DISABLED
* BUG#72118: BUG#18454679: PROMOTING A SLAVE AFTER A RESET MASTER HANGS
* BUG#72119: BUG#18454737 "GROUP ADD" HANGS WITH SERVER AS
  LOCALHOST:32274
* BUG#72149: BUG#18524482: EMPTY PASSWORD IN CONFIGURATION FILE LEADS TO
  ERRORS
* BUG#72338: BUG#18459012: COMMANDS FAIL IF THE "PROTOCOL.XMLRPC.USER"
  OPTION IS NOT PROVIDED
* BUG#72432: BUG#18458461: "MYSQLFABRIC MANAGE SETUP" RESULTS IN A LOST
  CONNECTION ERROR
* BUG#72553: BUG#18712020: CONCURRENCY CONTROL IS NOT LOCKING THE RIGHT
  OBJECTS
* BUG#72606: BUG#17747197: MYSQL FABRIC: FAILOVER SCENARIO FAILED FOR A
  GROUP
* Bug#18370927: BAD ERROR MESSAGE WHEN MYSQLDUMP NOT FOUND
* Bug#18370958: ERROR FOR WRONG ARGUMENT COUNT SHOULD SHOW COMMAND'S
  SYNOPSIS
* Bug#18458705: "MYSQLFABRIC MANAGE SETUP" RESULTS IN ERROR AFTER
  WINDOWS MSI INSTALLATION
* BUG#18477189: MYSQLFABRIC PARAMETERS NEED TO BE PASSED TO CMDS WHEN
  AUTHENTICATION IS ENABLED
* BUG#18648779: BUG#72448: FAILS TO REPLICATE FABRIC DATABASE USING NBD
  CLUSTER SETUP
* Bug#18824565: SHARD MOVE AND SPLIT FAILS IF PASSWORD IS PROVIDED FOR
  CLIENT IN FABRIC.CFG

Release 1.4.2 (released March 25, 2014)
---------------------------------------

* WL#7388: Failover/Switchover based on unreliable failure detectors
* WL#7455: Credentials for Fabric
* WL#7599: Cleaning up shard move and split semantics
* WL#7648: Decoupling provisioning from updates to state store
* BUG#71370: BUG#18087356: The prefix store.dump_* gives a false
  impression about update operations
* BUG#71448: BUG#18138545 - GROUP ADD FAILS IF ACCOUNT HAS NO ACCESS TO
  MYSQL SCHEMA
* BUG#71512: BUG#18153823: SERVERS IN THE SAME GROUP SHOULD USE A SINGLE
  USER/PASSWORD
* BUG#71525: BUG#17702237: IS_CONNECTED() IS CHECKED EVERY TIME A
  STATEMENT IS EXECUTED
* BUG#72117: BUG#18454582: SCHEDULER DOES NOT NOTIFY ALL PROCEDURES THAT
  ARE FREE TO GO AFTER A RELEASE
* BUG#17820905: Changed default TCP/IP port to 32274
* BUG#18124108: BUG#71428: FABRIC.SERVER.SET_STATUS() IS INCONSISTENT
  WITH FABRIC.STORE.DUMP_SERVERS()

Release 1.4.1 (released December 16, 2013)
------------------------------------------

* HAM-364: test_promote (test_replication_events.py) is failing
* WL#7401: Read only remote commands in Fabric should *NOT* pass through
  the executor
* WL#7423: Use the Shard Mapping ID for GLOBAL server lookups.
* BUG#70512: BUG#17555531: Windows source installation fails in trying
  to use /etc
* BUG#17454423: MySQLfabric script does not recognize commands on
  windows
* BUG#17592301: MYSQLFABRIC MANAGE START HANGS
* BUG#17633546: CHECKPOINT ROUTINES LEAD TO DEADLOCKS
* BUG#17639666: BUG#17655819: BUG#70694: MYSQLFABRIC IS NOT EXECUTABLE
  ON WINDOWS
* BUG#17804807: BUG#70924 SERVER OBJECT DOES NOT HAVE A CLEAN DESIGN TO
  REPRESENT SCALING OUT SERVERS
* Bug#17832848: BINARY DATA IN OUTPUT FROM STORE.DUMP_SHARD_INDEX ON
  HASH SHARD MAPPING

Release 1.4.0 (released September 04, 2013)
-------------------------------------------

* HAM-8: Improved the test.py and made it support logging and external
  libraries such as mysql.connector.
* HAM-18: Persister Management
* HAM-30: Implement event processing
* HAM-40: Remove deprecated decorators
* HAM-42: Command-Line Interface Module.
* HAM-52: Mismatch between service and logging.
* HAM-59: Clean up replication and high availability functions.
* HAM-61: Extend the server's properties and life-cycle.
* HAM-62: Define the appropriate concurrency control mechanism among
  procedures - Part II
* HAM-63: Implement compensating operations (Part-III).
* HAM-65: Fast Re-sharding HAM-125: Implement Global operations for
  FABRIC
* HAM-70: Created commands for master group management
* HAM-74: Add version checking
* HAM-78: Automatically configure an added server as slave.
* HAM-80: Documentation is not being generated.
* HAM-83: Adding commands for database sharding.
* HAM-85: Problems with --daemonize.
* HAM-86: Create command "fabric manage setup/teardown"
* HAM-87: Present results reported by a command in a user-friendly way
* HAM-88: setup.py is not installing the configuration file "main.cfg"
  in /etc/fabric
* HAM-90: Creating the fabric list mapping definitions command
* HAM-94: Mismatch between fabric and connector python
* HAM-95: setup.py is only installing docs from the build/ direcotry
* HAM-98: Instrument the code so that we can evaluate fabric performance
* HAM-100: Fixed documentation issues in the README and README.devel.
* HAM-102: MySQL Fabric manage stop hangs when we interrupt in the
  fabric start page HAM-103: Fabric manage setup hangs when the
  corresponding server is not started.
* HAM-108: Starting a failure detector re-register events. HAM-112:
  Remove "duplicate" commands from the interface.
* HAM-109: Replication topology fails after a switchover/promote.
* HAM-120: Incorrect error message while promoting a server again in a
  group. HAM-114: Promote fails after removing the previous master
  from the group. HAM-113: Promote fails after a demote.
* HAM-136: logger.setLevel("INFO") does not work with python 2.6
* HAM-140: Server Commands don't have access to config and options
  objects.
* HAM-160: Tests fail in jenkins due to wrong password
* HAM-161: Remove the distribute_datadir.py module.
* HAM-164: Tests that remove shards complain about message format
* HAM-170: test_check_no_healthy_slave is sporadically failing
* HAM-177: test_switch_master in test_mysql_replication.py fails
  sporadically
* HAM-180: Remove non-existent paths in main.cfg
* HAM-181: Use a pattern to check binary log names in the text cases.
* HAM-182: Refactoring/Renaming sharding schema
* HAM-183: Define a single interface to trigger either a switchover or
  failover
* HAM-184: Setting a server's status to FAULTY should trigger a
  failover.
* HAM-185: Setting a server's status to RUNNING should automatically
  make it a slave
* HAM-190: Extending the underlying framework for RANGE sharding to
  allow its usage in HASH based sharding.
* HAM-191: HASH based sharding.
* HAM-193: Stack traces are being printed out when it is not really
  necessary
* HAM-194: Group check_group_availability is showing below error if a
  server is downH
* HAM-201: Commands should return True to indicate success instead of
  False
* HAM-202: Some tests are failing in jenkins due to cleanup problems
* HAM-222: Use rotating log file by default
* HAM-239: Change name in code
* HAM-240: Fix PyLint errors in sharding code
* HAM-245: Move shard_mapping_id from shards to shard_ranges
* HAM-251: Fabric couldn't start because the main.cfg was not correctly
  installed and executor parameter was not found
* HAM-255: Dump Interface
* HAM-264: manage stop throws an exception
* HAM-267: There is no way to configure server and client individually
  from the same config
* HAM-269: Number of concurrent executors are not being set properly in
  mysqlfabric
* HAM-270: Sharding prune fails to delete proper rows in group tables
  HAM-272: Sharding Prune shows error with HASH base sharding
* HAM-271: No error message appear if the add_shard (any FABRIC command)
  command is wrong (having wrong number of parameters).
* HAM-285: Error is not proper if promote a faulty status servers in a
  group
* HAM-295: The install location of configuration file (main.cfg) changes
  for diff operating systems/distro HAM-205: Not able to Install
  Fabric in Windows machine
* HAM-300: Improve documentation of persistence system
* HAM-316: Configuration file should be in /etc/mysql.
* HAM-323: Server Dump interfaces not relfecting status for a faulty
  server - Add faulty server state
* HAM-324: Remove hard coding of server address and port number in the
  test_dump_interfaces test case
* HAM-327: Remove TODOs from the code
* HAM-340: Error executing mysqlfabric: Configuration file is not found
* HAM-350: Add support to dump interfaces for HASH based sharding
* WL#6123: Basic HA Manager Framework
* WL#6424: Configuration File Handling
* WL#6439: Sharding utility for offline sharding

Release 0.4.0 (released December 16, 2013)
------------------------------------------

* HAM-364: test_promote (test_replication_events.py) is failing
* WL#7401: Read only remote commands in Fabric should *NOT* pass through
  the executor
* WL#7423: Use the Shard Mapping ID for GLOBAL server lookups.
* BUG#70512: BUG#17555531: Windows source installation fails in trying
  to use /etc
* BUG#17454423: MySQLfabric script does not recognize commands on
  windows
* BUG#17592301: MYSQLFABRIC MANAGE START HANGS
* BUG#17633546: CHECKPOINT ROUTINES LEAD TO DEADLOCKS
* BUG#17639666: BUG#17655819: BUG#70694: MYSQLFABRIC IS NOT EXECUTABLE
  ON WINDOWS
* BUG#17804807: BUG#70924 SERVER OBJECT DOES NOT HAVE A CLEAN DESIGN TO
  REPRESENT SCALING OUT SERVERS
* Bug#17832848: BINARY DATA IN OUTPUT FROM STORE.DUMP_SHARD_INDEX ON
  HASH SHARD MAPPING

Release 0.3.0 (released September 04, 2013)
-------------------------------------------

* HAM-62: Define the appropriate concurrency control mechanism among
  procedures - Part II
* HAM-98: Instrument the code so that we can evaluate fabric performance
* HAM-181: Use a pattern to check binary log names in the text cases.
* HAM-182: Refactoring/Renaming sharding schema
* HAM-183: Define a single interface to trigger either a switchover or
  failover
* HAM-184: Setting a server's status to FAULTY should trigger a
  failover.
* HAM-185: Setting a server's status to RUNNING should automatically
  make it a slave
* HAM-190: Extending the underlying framework for RANGE sharding to
  allow its usage in HASH based sharding.
* HAM-191: HASH based sharding.
* HAM-193: Stack traces are being printed out when it is not really
  necessary
* HAM-194: Group check_group_availability is showing below error if a
  server is downH
* HAM-201: Commands should return True to indicate success instead of
  False
* HAM-202: Some tests are failing in jenkins due to cleanup problems
* HAM-222: Use rotating log file by default
* HAM-239: Change name in code
* HAM-240: Fix PyLint errors in sharding code
* HAM-245: Move shard_mapping_id from shards to shard_ranges
* HAM-251: Fabric couldn't start because the main.cfg was not correctly
  installed and executor parameter was not found
* HAM-255: Dump Interface
* HAM-264: manage stop throws an exception
* HAM-267: There is no way to configure server and client individually
  from the same config
* HAM-269: Number of concurrent executors are not being set properly in
  mysqlfabric
* HAM-270: Sharding prune fails to delete proper rows in group tables
  HAM-272: Sharding Prune shows error with HASH base sharding
* HAM-271: No error message appear if the add_shard (any FABRIC command)
  command is wrong (having wrong number of parameters).
* HAM-285: Error is not proper if promote a faulty status servers in a
  group
* HAM-295: The install location of configuration file (main.cfg) changes
  for diff operating systems/distro HAM-205: Not able to Install
  Fabric in Windows machine
* HAM-300: Improve documentation of persistence system
* HAM-316: Configuration file should be in /etc/mysql.
* HAM-323: Server Dump interfaces not relfecting status for a faulty
  server - Add faulty server state
* HAM-324: Remove hard coding of server address and port number in the
  test_dump_interfaces test case
* HAM-327: Remove TODOs from the code
* HAM-340: Error executing mysqlfabric: Configuration file is not found
* HAM-350: Add support to dump interfaces for HASH based sharding

Release 0.2.0 (released May 07, 2013)
-------------------------------------

* HAM-59: Clean up replication and high availability functions.
* HAM-63: Implement compensating operations (Part-III).
* HAM-65: Fast Re-sharding HAM-125: Implement Global operations for
  FABRIC
* HAM-140: Server Commands don't have access to config and options
  objects.
* HAM-160: Tests fail in jenkins due to wrong password
* HAM-161: Remove the distribute_datadir.py module.
* HAM-164: Tests that remove shards complain about message format
* HAM-170: test_check_no_healthy_slave is sporadically failing
* HAM-177: test_switch_master in test_mysql_replication.py fails
  sporadically
* HAM-180: Remove non-existent paths in main.cfg

Release 0.1.2 (released April 27, 2013)
---------------------------------------

* HAM-52: Mismatch between service and logging.
* HAM-74: Add version checking
* HAM-100: Fixed documentation issues in the README and README.devel.
* HAM-102: MySQL Fabric manage stop hangs when we interrupt in the
  fabric start page HAM-103: Fabric manage setup hangs when the
  corresponding server is not started.
* HAM-108: Starting a failure detector re-register events. HAM-112:
  Remove "duplicate" commands from the interface.
* HAM-109: Replication topology fails after a switchover/promote.
* HAM-120: Incorrect error message while promoting a server again in a
  group. HAM-114: Promote fails after removing the previous master
  from the group. HAM-113: Promote fails after a demote.
* HAM-136: logger.setLevel("INFO") does not work with python 2.6

Release 0.1.1 (released February 28, 2013)
------------------------------------------

* HAM-42: Command-Line Interface Module.
* HAM-70: Created commands for master group management
* HAM-80: Documentation is not being generated.
* HAM-83: Adding commands for database sharding.
* HAM-85: Problems with --daemonize.
* HAM-86: Create command "fabric manage setup/teardown"
* HAM-87: Present results reported by a command in a user-friendly way
* HAM-88: setup.py is not installing the configuration file "main.cfg"
  in /etc/fabric
* HAM-90: Creating the fabric list mapping definitions command
* HAM-94: Mismatch between fabric and connector python
* HAM-95: setup.py is only installing docs from the build/ direcotry

Release 0.1.0 (released January 23, 2013)
-----------------------------------------

* HAM-8: Improved the test.py and made it support logging and external
  libraries such as mysql.connector.
* HAM-18: Persister Management
* HAM-30: Implement event processing
* HAM-40: Remove deprecated decorators
* WL#6123: Basic HA Manager Framework
* WL#6424: Configuration File Handling
* WL#6439: Sharding utility for offline sharding
