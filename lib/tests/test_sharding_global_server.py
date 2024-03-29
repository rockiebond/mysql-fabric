#
# Copyright (c) 2013,2014, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#

import unittest
import tests.utils

from time import sleep
from tests.utils import MySQLInstances
from mysql.fabric import (
    executor as _executor,
    errors as _errors,
    replication as _replication,
)
from mysql.fabric.server import (
    MySQLServer,
    Group,
)

class TestShardingGlobalServer(unittest.TestCase):

    def assertStatus(self, status, expect):
        items = (item['diagnosis'] for item in status[1] if item['diagnosis'])
        self.assertEqual(status[1][-1]["success"], expect, "\n".join(items))

    def setUp(self):
        """Creates the following topology for testing,

        GROUPID1 - localhost:13001, localhost:13002 - Global Group
        GROUPID2 - localhost:13003, localhost:13004 - shard 1
        GROUPID3 - localhost:13005, localhost:13006 - shard 2
        """
        self.manager, self.proxy = tests.utils.setup_xmlrpc()

        status = self.proxy.group.create("GROUPID1", "First description.")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_create_group).")
        status = self.proxy.group.add(
            "GROUPID1", MySQLInstances().get_address(0)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")
        status = self.proxy.group.add(
            "GROUPID1", MySQLInstances().get_address(1)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")

        status = self.proxy.group.create("GROUPID2", "Second description.")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_create_group).")
        status = self.proxy.group.add(
            "GROUPID2", MySQLInstances().get_address(2)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")
        status = self.proxy.group.add(
            "GROUPID2", MySQLInstances().get_address(3)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")

        status = self.proxy.group.create("GROUPID3", "Third description.")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_create_group).")
        status = self.proxy.group.add(
            "GROUPID3", MySQLInstances().get_address(4)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")
        status = self.proxy.group.add(
            "GROUPID3", MySQLInstances().get_address(5)
        )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_server).")

        status = self.proxy.group.promote("GROUPID1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")
        status = self.proxy.group.promote("GROUPID2")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")
        status = self.proxy.group.promote("GROUPID3")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        status = self.proxy.sharding.create_definition("RANGE", "GROUPID1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_define_shard_mapping).")
        self.assertEqual(status[2], 1)

        status = self.proxy.sharding.add_table(1, "db1.t1", "userID1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_shard_mapping).")

        status = self.proxy.sharding.add_shard(1, "GROUPID2/0,GROUPID3/1001", "ENABLED")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_add_shard).")

    def test_global_lookup(self):
        """Basic test ensuring that doing a lookup with hint as GLOBAL
        returns the information of the Global Group.
        """
        #create the list of the expected servers
        expected_server_address_list = \
            [MySQLInstances().get_address(0), MySQLInstances().get_address(1)]

        #Perform the lookup
        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]

        #Ensure that the output of the lookup matches the expected list of
        #servers.
        obtained_address_list = [obtained_server_list[0][1],
                                obtained_server_list[1][1]]
        self.assertEqual(set(expected_server_address_list),
                                  set(obtained_address_list))

    def test_global_update_propogation(self):
        """Ensure the global updates are passed to all the shards.
        """

        #Lookup the global server and run some DDL statements
        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("DROP DATABASE IF EXISTS global_db")
        global_master.exec_stmt("CREATE DATABASE global_db")
        global_master.exec_stmt("CREATE TABLE global_db.global_table"
                                  "(userID INT, name VARCHAR(30))")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(101, 'TEST 1')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(202, 'TEST 2')")

        #Give some times for replication to update the shards
        sleep(3)

        #Lookup and verify that the data is updated in the other shards.
        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                rows = shard_server.exec_stmt(
                    "SELECT NAME FROM global_db.global_table", {"fetch" : True}
                )
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                rows = shard_server.exec_stmt(
                    "SELECT NAME FROM global_db.global_table", {"fetch" : True}
                )
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')

    def test_global_update_propogation_switchover(self):
        """Ensure that the global data propogation is not impacted when a
        switchover is triggered. Basically it should ensure that the new
        master is redirected to replicate to all the other shards.
        """
        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("DROP DATABASE IF EXISTS global_db")
        global_master.exec_stmt("CREATE DATABASE global_db")
        global_master.exec_stmt("CREATE TABLE global_db.global_table"
                                  "(userID INT, name VARCHAR(30))")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(101, 'TEST 1')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(202, 'TEST 2')")

        status = self.proxy.group.promote("GROUPID1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        sleep(5)

        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(303, 'TEST 3')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(404, 'TEST 4')")

        status = self.proxy.group.promote("GROUPID2")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        sleep(5)

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(505, 'TEST 5')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(606, 'TEST 6')")

        status = self.proxy.group.promote("GROUPID3")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        sleep(5)

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(505, 'TEST 7')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(606, 'TEST 8')")

        sleep(5)

        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                rows = shard_server.exec_stmt(
                    "SELECT NAME FROM global_db.global_table", {"fetch" : True}
                )
                self.assertEqual(len(rows), 8)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')
                self.assertEqual(rows[2][0], 'TEST 3')
                self.assertEqual(rows[3][0], 'TEST 4')
                self.assertEqual(rows[4][0], 'TEST 5')
                self.assertEqual(rows[5][0], 'TEST 6')
                self.assertEqual(rows[6][0], 'TEST 7')
                self.assertEqual(rows[7][0], 'TEST 8')

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                rows = shard_server.exec_stmt(
                    "SELECT NAME FROM global_db.global_table", {"fetch" : True}
                )
                self.assertEqual(len(rows), 8)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')
                self.assertEqual(rows[2][0], 'TEST 3')
                self.assertEqual(rows[3][0], 'TEST 4')
                self.assertEqual(rows[4][0], 'TEST 5')
                self.assertEqual(rows[5][0], 'TEST 6')
                self.assertEqual(rows[6][0], 'TEST 7')
                self.assertEqual(rows[7][0], 'TEST 8')

    def test_global_update_propogation_failover(self):
        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
            else:
                global_slave_uuid = obtained_server_list[idx][0]

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("DROP DATABASE IF EXISTS global_db")
        global_master.exec_stmt("CREATE DATABASE global_db")
        global_master.exec_stmt("CREATE TABLE global_db.global_table"
                                  "(userID INT, name VARCHAR(30))")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(101, 'TEST 1')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(202, 'TEST 2')")

        status = self.proxy.group.promote(
            "GROUPID1", global_slave_uuid
            )
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        sleep(5)

        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(303, 'TEST 3')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(404, 'TEST 4')")

        status = self.proxy.group.lookup_servers("GROUPID2")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]

        for idx in range(0, 2):
            if obtained_server_list[idx]["status"] == MySQLServer.SECONDARY:
                slave_uuid = obtained_server_list[idx]["server_uuid"]
                break

        status = self.proxy.group.promote("GROUPID2", str(slave_uuid))
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        sleep(5)

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(505, 'TEST 5')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(606, 'TEST 6')")

        status = self.proxy.group.lookup_servers("GROUPID3")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx]["status"] == MySQLServer.SECONDARY:
                slave_uuid = obtained_server_list[idx]["server_uuid"]
                break

        status = self.proxy.group.promote("GROUPID3", str(slave_uuid))
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_change_to_candidate).")

        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(505, 'TEST 7')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(606, 'TEST 8')")

        sleep(5)

        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            shard_uuid = obtained_server_list[idx][0]
            shard_server = MySQLServer.fetch(shard_uuid)
            shard_server.connect()
            rows = shard_server.exec_stmt(
                                    "SELECT NAME FROM global_db.global_table",
                                    {"fetch" : True})
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[0][0], 'TEST 1')
            self.assertEqual(rows[1][0], 'TEST 2')
            self.assertEqual(rows[2][0], 'TEST 3')
            self.assertEqual(rows[3][0], 'TEST 4')
            self.assertEqual(rows[4][0], 'TEST 5')
            self.assertEqual(rows[5][0], 'TEST 6')
            self.assertEqual(rows[6][0], 'TEST 7')
            self.assertEqual(rows[7][0], 'TEST 8')

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            shard_uuid = obtained_server_list[idx][0]
            shard_server = MySQLServer.fetch(shard_uuid)
            shard_server.connect()
            rows = shard_server.exec_stmt(
                                    "SELECT NAME FROM global_db.global_table",
                                    {"fetch" : True})
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[0][0], 'TEST 1')
            self.assertEqual(rows[1][0], 'TEST 2')
            self.assertEqual(rows[2][0], 'TEST 3')
            self.assertEqual(rows[3][0], 'TEST 4')
            self.assertEqual(rows[4][0], 'TEST 5')
            self.assertEqual(rows[5][0], 'TEST 6')
            self.assertEqual(rows[6][0], 'TEST 7')
            self.assertEqual(rows[7][0], 'TEST 8')

    def test_shard_disable(self):
        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server_1 = MySQLServer.fetch(shard_uuid)
                shard_server_1.connect()

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server_2 = MySQLServer.fetch(shard_uuid)
                shard_server_2.connect()

        self.proxy.sharding.disable_shard("1")
        self.proxy.sharding.disable_shard("2")

        sleep(3)

        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("DROP DATABASE IF EXISTS global_db")
        global_master.exec_stmt("CREATE DATABASE global_db")
        global_master.exec_stmt("CREATE TABLE global_db.global_table"
                                  "(userID INT, name VARCHAR(30))")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(101, 'TEST 1')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(202, 'TEST 2')")

        sleep(3)

        try:
            shard_server_1.exec_stmt(
                "SELECT NAME FROM global_db.global_table", {"fetch" : True}
                )
            raise Exception("Disable Shard failed to remove shard.")
        except _errors.DatabaseError:
            #Expected
            pass

        try:
            shard_server_2.exec_stmt(
                "SELECT NAME FROM global_db.global_table", {"fetch" : True}
            )
            raise Exception("Disable Shard failed to remove shard.")
        except _errors.DatabaseError:
            #Expected
            pass

    def test_shard_enable(self):
        self.proxy.sharding.disable_shard("1")
        self.proxy.sharding.disable_shard("2")

        sleep(5)

        self.proxy.sharding.enable_shard("1")
        self.proxy.sharding.enable_shard("2")

        sleep(3)

        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                global_master_uuid = obtained_server_list[idx][0]
                break

        global_master = MySQLServer.fetch(global_master_uuid)
        global_master.connect()

        global_master.exec_stmt("DROP DATABASE IF EXISTS global_db")
        global_master.exec_stmt("CREATE DATABASE global_db")
        global_master.exec_stmt("CREATE TABLE global_db.global_table"
                                  "(userID INT, name VARCHAR(30))")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(101, 'TEST 1')")
        global_master.exec_stmt("INSERT INTO global_db.global_table "
                                  "VALUES(202, 'TEST 2')")

        sleep(3)

        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]

        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                try:
                    rows = shard_server.exec_stmt(
                        "SELECT NAME FROM global_db.global_table",
                        {"fetch" : True}
                    )
                except _errors.DatabaseError:
                    raise Exception("Enable Shard failed to enable shard.")
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                try:
                    rows = shard_server.exec_stmt(
                        "SELECT NAME FROM global_db.global_table",
                        {"fetch" : True}
                    )
                except _errors.DatabaseError:
                    raise Exception("Enable Shard failed to enable shard.")
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0][0], 'TEST 1')
                self.assertEqual(rows[1][0], 'TEST 2')

    def test_switchover_with_no_master(self):
        """Ensure that a switchover/failover happens when masters in the
        shard and global groups are dead.
        """
        # Check that a shard group has it master pointing to a the master
        # in the global group.
        global_group = Group.fetch("GROUPID1")
        shard_group = Group.fetch("GROUPID2")
        other_shard_group = Group.fetch("GROUPID3")
        global_master = MySQLServer.fetch(global_group.master)
        global_master.connect()
        shard_master = MySQLServer.fetch(shard_group.master)
        shard_master.connect()
        other_shard_master = MySQLServer.fetch(other_shard_group.master)
        other_shard_master.connect()
        self.assertEqual(
            _replication.slave_has_master(shard_master),
            str(global_group.master)
        )
        self.assertEqual(
            _replication.slave_has_master(other_shard_master),
            str(global_group.master)
        )

        # Demote the master in the global group and check that a
        # shard group points to None.
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, global_master.uuid)
        self.proxy.group.demote("GROUPID1")
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, None)
        self.assertEqual(_replication.slave_has_master(shard_master), None)
        self.assertEqual(
            _replication.slave_has_master(other_shard_master), None
        )

        # Demote the master in a shard group and promote the master
        # in the global group.
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, None)
        shard_group = Group.fetch("GROUPID2")
        self.assertEqual(shard_group.master, shard_master.uuid)
        self.proxy.group.demote("GROUPID2")
        shard_group = Group.fetch("GROUPID2")
        self.assertEqual(shard_group.master, None)
        self.proxy.group.promote("GROUPID1", str(global_master.uuid))
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, global_master.uuid)
        self.assertEqual(_replication.slave_has_master(shard_master), None)
        self.assertEqual(
            _replication.slave_has_master(other_shard_master),
            str(global_group.master)
        )

        # Promote the master in the previous shard group and check that
        # everything is back to normal.
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, global_master.uuid)
        self.assertEqual(_replication.slave_has_master(shard_master), None)
        shard_group = Group.fetch("GROUPID2")
        self.assertEqual(shard_group.master, None)
        self.proxy.group.promote("GROUPID2", str(shard_master.uuid))
        self.assertEqual(
            _replication.slave_has_master(shard_master),
            str(global_group.master)
        )
        self.assertEqual(
            _replication.slave_has_master(other_shard_master),
            str(global_group.master)
        )
        shard_group = Group.fetch("GROUPID2")
        self.assertEqual(shard_group.master, shard_master.uuid)

        # Demote the master in the global group, check that a shard group
        # points to None, promot it again and check that everything is back
        # to normal
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, global_master.uuid)
        shard_group = Group.fetch("GROUPID2")
        self.assertEqual(shard_group.master, shard_master.uuid)
        self.proxy.group.demote("GROUPID1")
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, None)
        self.assertEqual(_replication.slave_has_master(shard_master), None)
        self.proxy.group.promote("GROUPID1", str(global_master.uuid))
        global_group = Group.fetch("GROUPID1")
        self.assertEqual(global_group.master, global_master.uuid)
        self.assertEqual(
            _replication.slave_has_master(shard_master),
            str(global_group.master)
        )
        self.assertEqual(
            _replication.slave_has_master(other_shard_master),
            str(global_group.master)
        )

    def tearDown(self):
        self.proxy.sharding.enable_shard("1")
        self.proxy.sharding.enable_shard("2")

        status = self.proxy.sharding.lookup_servers("1", 500,  "GLOBAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                shard_server.exec_stmt("DROP DATABASE IF EXISTS global_db")

        status = self.proxy.sharding.lookup_servers("db1.t1", 500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                shard_server.exec_stmt("DROP DATABASE IF EXISTS global_db")

        status = self.proxy.sharding.lookup_servers("db1.t1", 1500,  "LOCAL")
        self.assertEqual(status[0], True)
        self.assertEqual(status[1], "")
        obtained_server_list = status[2]
        for idx in range(0, 2):
            if obtained_server_list[idx][2]:
                shard_uuid = obtained_server_list[idx][0]
                shard_server = MySQLServer.fetch(shard_uuid)
                shard_server.connect()
                shard_server.exec_stmt("DROP DATABASE IF EXISTS global_db")

        status = self.proxy.sharding.disable_shard("1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_disable_shard).")

        status = self.proxy.sharding.disable_shard("2")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_disable_shard).")

        status = self.proxy.sharding.remove_shard("1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_remove_shard).")

        status = self.proxy.sharding.remove_shard("2")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_remove_shard).")

        status = self.proxy.sharding.remove_table("db1.t1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_remove_shard_mapping).")

        status = self.proxy.sharding.remove_definition("1")
        self.assertStatus(status, _executor.Job.SUCCESS)
        self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
        self.assertEqual(status[1][-1]["description"],
                         "Executed action (_remove_shard_mapping_defn).")

        #self.proxy.sharding.disable_shard("3")
        self.proxy.group.demote("GROUPID1")
        self.proxy.group.demote("GROUPID2")
        self.proxy.group.demote("GROUPID3")
        for group_id in ("GROUPID1", "GROUPID2", "GROUPID3"):
            status = self.proxy.group.lookup_servers(group_id)
            self.assertEqual(status[0], True)
            self.assertEqual(status[1], "")
            obtained_server_list = status[2]
            status = \
                self.proxy.group.remove(
                    group_id, obtained_server_list[0]["server_uuid"]
                )
            self.assertStatus(status, _executor.Job.SUCCESS)
            self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
            self.assertEqual(status[1][-1]["description"],
                             "Executed action (_remove_server).")
            status = \
                 self.proxy.group.remove(
                     group_id, obtained_server_list[1]["server_uuid"]
                 )
            self.assertStatus(status, _executor.Job.SUCCESS)
            self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
            self.assertEqual(status[1][-1]["description"],
                             "Executed action (_remove_server).")
            status = self.proxy.group.destroy(group_id)
            self.assertStatus(status, _executor.Job.SUCCESS)
            self.assertEqual(status[1][-1]["state"], _executor.Job.COMPLETE)
            self.assertEqual(status[1][-1]["description"],
                             "Executed action (_destroy_group).")

        tests.utils.cleanup_environment()
        tests.utils.teardown_xmlrpc(self.manager, self.proxy)
