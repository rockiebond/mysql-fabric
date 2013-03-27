"""This module provides the necessary interfaces for performing administrative
tasks on groups and servers, specifically MySQL Servers.

It should be possible to add, update and remove a group. One cannot, however,
remove a group if there are associated servers. It should also be possible to
add a server to a group and remove a server from a group.

Search functions are also provided so that one may look up groups and servers.
Given a server's address, one may also find out the server's uuid if the server
is alive and kicking.

Functions are scheduled to be asynchronously executed and return a schedule's
description, i.e. a job's description. If users are not interestered in the
result produced by a function, they must set the synchronous parameter to false.
It is set to true by default which means that the call is blocked until the
execution finishes.

The scheduling is made through the executor which enqueues functions, namely
jobs, and then serializes their execution within a Fabric Server. Any job object
encapsulates a function to be executed, its parameters, its execution's status
and its result. Due to its asynchronous nature, a job accesses a snapshot
produced by previously executed functions which are atomically processed so that
Fabric is never left in an inconsistent state after a failure.

Functions always return results in the following format::

  str(job.uuid), job.status, job.result

It is worth noticing that this module only provides functions for performing
basic administrative tasks, provisioning and high-availability functions are
provided elsewhere.
"""
import logging
import uuid as _uuid

import mysql.hub.events as _events
import mysql.hub.server as _server
import mysql.hub.errors as _errors
import mysql.hub.failure_detector as _detector

from mysql.hub.command import (
    ProcedureCommand,
    )

_LOGGER = logging.getLogger("mysql.hub.services.server")

LOOKUP_GROUPS = _events.Event()
class GroupLookups(ProcedureCommand):
    """Return information on existing group(s).
    """
    group_name = "group"
    command_name = "lookup_groups"

    def execute(self, group_id=None, synchronous=True):
        """Return information on existing group(s).

        :param group_id: None if one wants to list the existing groups or
                         group's id if one wants information on a group.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: List with existing groups or detailed information on group.
        :rtype: [[group], ....] or {group_id : ..., description : ...}.
        """
        procedures = _events.trigger(LOOKUP_GROUPS, group_id)
        return self.wait_for_procedures(procedures, synchronous)

CREATE_GROUP = _events.Event()
class GroupCreate(ProcedureCommand):
    """Create a group.
    """
    group_name = "group"
    command_name = "create"

    def execute(self, group_id, description=None, synchronous=True):
        """Create a group.

        :param group_id: Group's id.
        :param description: Group's description.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(CREATE_GROUP, group_id, description)
        return self.wait_for_procedures(procedures, synchronous)

UPDATE_GROUP = _events.Event()
class GroupDescription(ProcedureCommand):
    """Update group's description.
    """
    group_name = "group"
    command_name = "description"

    def execute(self, group_id, description=None, synchronous=True):
        """Update group's description.

        :param group_id: Group's id.
        :param description: Group's description.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(UPDATE_GROUP, group_id, description)
        return self.wait_for_procedures(procedures, synchronous)

REMOVE_GROUP = _events.Event()
class RemoveGroup(ProcedureCommand):
    """Remove a group.
    """
    group_name = "group"
    command_name = "destroy"

    def execute(self, group_id, force=False, synchronous=True):
        """Remove a group.

        :param group_id: Group's id.
        :param force: If the group is not empty, remove it serves.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(REMOVE_GROUP, group_id, force)
        return self.wait_for_procedures(procedures, synchronous)

LOOKUP_SERVERS = _events.Event()
class ServerLookups(ProcedureCommand):
    """Return information on existing server(s) in a group.
    """ 
    group_name = "group"
    command_name = "lookup_servers"

    def execute(self, group_id, uuid=None, synchronous=True):
        """Return information on existing server(s) in a group.

        :param group_id: Group's id.
        :param server_id: None if one wants to list the existing servers
                          in a group or server's id if one wants information
                          on a server in a group.
        :param synchronous: Whether one should wait until the execution
                            finishes or not.
        :return: List with existing severs in a group or detailed information
                 on a server in a group.
        :rtype: [server_uuid, ....] or  {"uuid" : uuid, "address": address,
                "user": user, "passwd": passwd}

        If the group does not exist, the :class:`mysqly.hub.errors.GroupError`
        exception is thrown.
        """
        procedures = _events.trigger(LOOKUP_SERVERS, group_id, uuid)
        return self.wait_for_procedures(procedures, synchronous)

LOOKUP_UUID = _events.Event()
class ServerUuid(ProcedureCommand):
    """Return server's uuid.
    """
    group_name = "server"
    command_name = "lookup_uuid"

    def execute(self, address, user, passwd, synchronous=True):
        """Retrieve server's uuid.

        :param address: Server's address.
        :param user: Server's user.
        :param passwd: Server's passwd.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: uuid.
        """
        procedures = _events.trigger(LOOKUP_UUID, address, user, passwd)
        return self.wait_for_procedures(procedures, synchronous)

CREATE_SERVER = _events.Event()
class ServerCreate(ProcedureCommand):
    """Add a server to a group.
    """
    group_name = "group"
    command_name = "add"

    def execute(self, group_id, address, user, passwd, synchronous=True):
        """Create a server and add it into a group.

        :param group_id: Group's id.
        :param address: Server's address.
        :param user: Server's user.
        :param passwd: Server's passwd.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(
            CREATE_SERVER, group_id, address, user, passwd
            )
        return self.wait_for_procedures(procedures, synchronous)

REMOVE_SERVER = _events.Event()
class ServerRemove(ProcedureCommand):
    """Remove a server from a group.
    """
    group_name = "group"
    command_name = "remove"

    def execute(self, group_id, uuid, synchronous=True):
        """Remove a server from a group.

        :param uuid: Server's uuid.
        :param group_id: Group's id.
        :param synchronous: Whether one should wait until the execution finishes
                            or not.
        :return: Tuple with job's uuid and status.
        """
        procedures = _events.trigger(REMOVE_SERVER, group_id, uuid)
        return self.wait_for_procedures(procedures, synchronous)

@_events.on_event(LOOKUP_GROUPS)
def _lookup_groups(group_id):
    """Return a list of existing groups or fetch information on a group
    identified by group_id.
    """
    if group_id is None:
        return _server.Group.groups()
    
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id))

    return {"group_id" : group.group_id,
            "description": group.description if group.description else ""}

@_events.on_event(CREATE_GROUP)
def _create_group(group_id, description):
    """Create group.
    """
    group = _server.Group.add(group_id, description)
    _LOGGER.debug("Added group (%s).", str(group))
    _detector.FailureDetector.register_group(group_id)

@_events.on_event(UPDATE_GROUP)
def _update_group_description(group_id, description):
    """Update a group description."""
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id))
    group.description = description
    _LOGGER.debug("Updated group (%s).", str(group))

@_events.on_event(REMOVE_GROUP)
def _remove_group(group_id, force):
    """Remove a group."""
    group = _server.Group.fetch(group_id)
    servers_uuid = []
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id, ))
    servers = group.servers()
    if servers and force:
        for server in servers:
            servers_uuid.append(server.uuid)
            _do_remove_server(group, server)
    elif servers:
        raise _errors.GroupError("Group (%s) is not empty." % (group_id, ))
    group.remove()
    cnx_pool = _server.ConnectionPool()
    for uuid in servers_uuid:
        cnx_pool.purge_connections(uuid)
    _LOGGER.debug("Removed group (%s).", str(group))
    _detector.FailureDetector.unregister_group(group_id)

@_events.on_event(LOOKUP_SERVERS)
def _lookup_servers(group_id, uuid=None):
    """Return existing servers in a group or information on a server.
    """
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id, ))

    if uuid is None:
        ret = []
        for server in group.servers():
            ret.append([str(server.uuid), server.address,
                       group.master == server.uuid])
        return ret

    if not group.contains_server(uuid):
        raise _errors.GroupError("Group (%s) does not contain server (%s)." \
                                 % (group_id, uuid))

    server = _server.MySQLServer.fetch(uuid)
    return {"uuid": str(server.uuid), "address": server.address,
            "user": server.user, "passwd": server.passwd}

@_events.on_event(LOOKUP_UUID)
def _lookup_uuid(address, user, passwd):
    """Retrieve server's uuid.
    """
    return _server.MySQLServer.discover_uuid(address=address, user=user,
                                             passwd=passwd)

@_events.on_event(CREATE_SERVER)
def _create_server(group_id, address, user, passwd):
    """Create a server and add it to a group.
    """
    uuid = _server.MySQLServer.discover_uuid(address=address, user=user,
                                             passwd=passwd)
    uuid = _uuid.UUID(uuid)
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id))
    if group.contains_server(uuid):
        raise _errors.ServerError("Server (%s) already exists in group (%s)." \
                                  % (str(uuid), group_id))
    server = _server.MySQLServer.add(uuid, address, user, passwd)
    server.connect()

    if not server.check_version_compat((5,6,8)):
        raise _errors.ServerError(
            "Server (%s) has an outdated version (%s). 5.6.8 or greater "
            "is required." % (uuid, server.version)
            )
    if not server.has_root_privileges():
        _LOGGER.warning(
            "User (%s) needs root privileges on Server (%s, %s)."
            % (user, address, uuid)
            )
        server.disconnect()

    group.add_server(server)
    _LOGGER.debug("Added server (%s) to group (%s).", str(server), str(group))

@_events.on_event(REMOVE_SERVER)
def _remove_server(group_id, uuid):
    """Remove a server from a group but check some requirements first."""
    uuid = _uuid.UUID(uuid)
    group = _server.Group.fetch(group_id)
    if not group:
        raise _errors.GroupError("Group (%s) does not exist." % (group_id))
    if not group.contains_server(uuid):
        raise _errors.GroupError("Group (%s) does not contain server (%s)." \
                                 % (group_id, uuid))
    if group.master == uuid:
        raise _errors.ServerError("Cannot remove server (%s), which is master "
                                  "in group (%s). Please, demote it first."
                                  % (uuid, group_id))
    server = _server.MySQLServer.fetch(uuid)
    _do_remove_server(group, server)
    _server.ConnectionPool().purge_connections(uuid)

def _do_remove_server(group, server):
    """Remove a server from a group."""
    group.remove_server(server)
    server.remove()
    _LOGGER.debug("Removed server (%s) from group (%s).", str(server),
                  str(group))
