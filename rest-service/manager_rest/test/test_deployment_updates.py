#########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
import os

import re

from nose.plugins.attrib import attr
from nose.tools import nottest

from manager_rest import archiving
from manager_rest.test import base_test
from cloudify_rest_client.exceptions import CloudifyClientError
from utils import get_resource as resource


@attr(client_min_version=2.1, client_max_version=base_test.LATEST_API_VERSION)
class DeploymentUpdatesTestCase(base_test.BaseServerTestCase):

    def test_get_empty(self):
        result = self.client.deployment_updates.list()
        self.assertEquals(0, len(result))

    def test_step_add(self):
        deployment_id = 'dep'
        self._deploy_base(deployment_id, 'no_output.yaml')
        step = {'action': 'add',
                'entity_type': 'output',
                'entity_id': 'outputs:custom_output'}

        self._update(deployment_id, 'one_output.yaml')
        dep_update = \
            self.client.deployment_updates.list(deployment_id=deployment_id)[0]
        self.assertEqual(1, len(dep_update.steps))
        self.assertDictContainsSubset(step, dep_update.steps[0])

    def test_step_remove(self):
        deployment_id = 'dep'
        self._deploy_base(deployment_id, 'one_output.yaml')
        step = {'action': 'remove',
                'entity_type': 'output',
                'entity_id': 'outputs:custom_output'}

        self._update(deployment_id, 'no_output.yaml')
        dep_update = \
            self.client.deployment_updates.list(deployment_id=deployment_id)[0]
        self.assertEqual(1, len(dep_update.steps))
        self.assertDictContainsSubset(step, dep_update.steps[0])

    def test_step_modify(self):
        deployment_id = 'dep'
        self._deploy_base(deployment_id, 'one_output.yaml')
        step = {'action': 'modify',
                'entity_type': 'output',
                'entity_id': 'outputs:custom_output'}

        self._update(deployment_id, 'change_output.yaml')
        dep_update = \
            self.client.deployment_updates.list(deployment_id=deployment_id)[0]
        self.assertEqual(1, len(dep_update.steps))
        self.assertDictContainsSubset(step, dep_update.steps[0])

    def test_one_active_update_per_deployment(self):
        deployment_id = 'dep'
        self._deploy_base(deployment_id, 'no_output.yaml')
        self._update(deployment_id, 'one_output.yaml')
        response = self._update(deployment_id,
                                blueprint_name='one_output.yaml')
        self.assertEquals(response.json['error_code'], 'conflict_error')
        self.assertIn('is not committed yet', response.json['message'])

        print response

    def test_workflow_and_skip_conflict(self):
        deployment_id = 'dep'
        self._deploy_base(deployment_id, 'no_output.yaml')

        msg = ('skip_install has been set to {skip_install}, skip uninstall '
               'has been set to {skip_uninstall}, and a custom workflow {'
               'workflow_id} has been set to replace "update". However, '
               'skip_install and skip_uninstall are mutually exclusive '
               'with a custom workflow')

        conflicting_params_list = [
            {
                'skip_install': True,
                'skip_uninstall': True,
                'workflow_id': 'custom_workflow'
            },
            {
                'skip_install': True,
                'skip_uninstall': False,
                'workflow_id': 'custom_workflow'
            },
            {
                'skip_install': False,
                'skip_uninstall': True,
                'workflow_id': 'custom_workflow'
            },
        ]

        for conflicting_params in conflicting_params_list:
            response = self._update(blueprint_name='no_output.yaml',
                                    deployment_id=deployment_id,
                                    **conflicting_params)
            self.assertEquals(response.json['message'],
                              msg.format(**conflicting_params))

    def _deploy_base(self,
                     deployment_id,
                     blueprint_name,
                     inputs=None):
        blueprint_path = os.path.join('resources',
                                      'deployment_update',
                                      'depup_step')
        self.put_deployment(deployment_id,
                            inputs=inputs,
                            blueprint_file_name=blueprint_name,
                            blueprint_dir=blueprint_path)

    def _update(self,
                deployment_id,
                blueprint_name,
                **kwargs):
        blueprint_path = resource(os.path.join('deployment_update',
                                               'depup_step'))

        archive_path = self.archive_mock_blueprint(
            archive_func=archiving.make_tarbz2file,
            blueprint_dir=blueprint_path)
        kwargs['application_file_name'] = blueprint_name

        return self.post_file('/deployment-updates/{0}/update/initiate'
                              .format(deployment_id),
                              archive_path,
                              query_params=kwargs)


@nottest
class DeploymentUpdatesStepAndStageTestCase(base_test.BaseServerTestCase):
    def test_step_invalid_operation(self):
        deployment_id = 'dep'
        deployment_update_id = self._stage(deployment_id).id
        step = {'action': 'illegal_operation',
                'entity_type': 'node',
                'entity_id': 'site1'}
        self.assertRaisesRegexp(CloudifyClientError,
                                'illegal modification operation',
                                self.client.deployment_updates.step,
                                deployment_update_id,
                                **step)

    def test_step_non_existent_entity_id(self):
        deployment_id = 'dep'
        deployment_update_id = self._stage(deployment_id).id

        non_existing_entity_id_steps = [
            # nodes
            {'action': 'add',
             'entity_type': 'node',
             'entity_id': 'nodes:non_existent_id'},
            {'action': 'remove',
             'entity_type': 'node',
             'entity_id': 'nodes:non_existent_id'},

            # relationships
            {'action': 'add',
             'entity_type': 'relationship',
             'entity_id': 'nodes:site1:relationships:[1]'},
            {'action': 'remove',
             'entity_type': 'relationship',
             'entity_id': 'nodes:site1:relationships:[1]'},

            # relationship operations
            {'action': 'add',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:relationships:[1]:source_operations:'
                          'cloudify.interfaces.relationship_lifecycle'
                          '.establish'},
            {'action': 'remove',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:relationships:[1]:source_operations:'
                          'cloudify.interfaces.relationship_lifecycle'
                          '.establish'},
            {'action': 'modify',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:relationships:[1]:source_operations:'
                          'cloudify.interfaces.relationship_lifecycle'
                          '.establish'},

            # node operations
            {'action': 'add',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:operations:'
                          'cloudify.interfaces.lifecycle.create1'},
            {'action': 'remove',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:operations:'
                          'cloudify.interfaces.lifecycle.create1'},
            {'action': 'modify',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:operations:'
                          'cloudify.interfaces.lifecycle.create1'},

            # properties
            {'action': 'add',
             'entity_type': 'property',
             'entity_id': 'nodes:site1:properties:ip'},
            {'action': 'remove',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:properties:ip'},
            {'action': 'modify',
             'entity_type': 'action',
             'entity_id': 'nodes:site1:properties:ip'},

        ]

        for step in non_existing_entity_id_steps:
            try:
                self.client.deployment_updates.step(deployment_update_id,
                                                    **step)
            except CloudifyClientError as e:
                self.assertEqual(e.status_code, 400)
                self.assertEqual(e.error_code,
                                 'unknown_modification_stage_error')
                self.assertIn(
                        "Entity type {0} with entity id {1}:"
                        .format(step['entity_type'], step['entity_id']),
                        e.message)
                break
            self.fail("entity id {0} of entity type {1} shouldn't be valid"
                      .format(step['entity_id'], step['entity_type']))

    def test_stage(self):
        deployment_id = 'dep'

        dep_update = self._stage(deployment_id)

        self.assertEquals('staged', dep_update.state)
        self.assertEquals(deployment_id, dep_update.deployment_id)

        # assert that deployment update id has deployment id prefix
        dep_up_id_regex = re.compile('^{0}-'.format(deployment_id))
        self.assertRegexpMatches(dep_update.id, re.compile(dep_up_id_regex))

        # assert steps list is initialized and empty
        self.assertListEqual([], dep_update.steps)

    def test_step_non_existent_entity_type(self):
        deployment_id = 'dep'
        deployment_update_id = self._stage(deployment_id).id
        step = {'action': 'add',
                'entity_type': 'non_existent_type',
                'entity_id': 'site1'}

        self.assertRaisesRegexp(CloudifyClientError,
                                'illegal modification entity type',
                                self.client.deployment_updates.step,
                                deployment_update_id,
                                **step)