# Created on 2014.06.30
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest
from ldap3 import Server, Connection, ServerPool, STRATEGY_REUSABLE_THREADED, GET_DSA_INFO, LDAPExtensionError
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, \
    test_lazy_connection, test_server_context, test_server_mode, test_pooling_strategy, test_pooling_active, \
    test_pooling_exhaust, test_server_edir_name, random_id, get_connection, drop_connection, add_user

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(check_names=True)
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-3'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-4'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-5'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-6'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-7'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-8'))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_who_am_i_extension(self):
        if not self.connection.strategy.pooled:
            try:
                if not self.connection.server.info:
                    self.connection.refresh_server_info()
                self.connection.extend.standard.who_am_i()
                result = self.connection.result
                self.assertTrue(result['description'] in ['success', 'protocolError'])
            except LDAPExtensionError as e:
                if not e.args[0] == 'extension not in DSA list of supported extensions':
                    raise

    def test_get_bind_dn_extension(self):
        if not self.connection.strategy.pooled:
            result = self.connection.extend.novell.get_bind_dn()
            self.assertTrue(test_user in result)

    def test_paged_search_accumulator(self):
        responses = self.connection.extend.standard.paged_search('o=test', '(cn=' + testcase_id + 'paged_search-*)', generator=False, paged_size=3)
        self.assertTrue(len(responses) == 8)

    def test_paged_search_generator(self):
        responses = []
        for response in self.connection.extend.standard.paged_search('o=test', '(cn=' + testcase_id + 'paged_search-*)'):
            responses.append(response)
        self.assertTrue(len(responses) == 8)

    def test_novell_list_replicas(self):
        result = self.connection.extend.novell.list_replicas('cn=' + test_server_edir_name + ',' + test_server_context)

        self.assertEqual(result, None)

    def test_novell_replica_info(self):
        result = self.connection.extend.novell.replica_info('cn=' + test_server_edir_name + ',' + test_server_context, '')

        self.assertEqual(result, '')

    def test_novell_partition_entry_count(self):
        result = self.connection.extend.novell.partition_entry_count('o=test')
        self.assertTrue(result > 60)