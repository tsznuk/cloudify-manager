########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

from cloudify.utils import ManagerVersion

METADATA_FILENAME = 'metadata.json'
M_VERSION = 'snapshot_version'
M_SCHEMA_REVISION = 'schema_revision'
M_STAGE_SCHEMA_REVISION = 'stage_schema_revision'
M_COMPOSER_SCHEMA_REVISION = 'composer_schema_revision'
M_HAS_CLOUDIFY_EVENTS = 'has_cloudify_events'
ARCHIVE_CERT_DIR = 'ssl'
INTERNAL_CERT_FILENAME = 'cloudify_internal_cert.pem'
INTERNAL_KEY_FILENAME = 'cloudify_internal_key.pem'
INTERNAL_P12_FILENAME = 'cloudify_internal.p12'
BROKER_DEFAULT_VHOST = '/'
DEFAULT_TENANT_NAME = 'default_tenant'
SECRET_STORE_AGENT_KEY_PREFIX = 'cfyagent_key__'
STAGE_BASE_FOLDER = '/opt/cloudify-stage'
STAGE_CONFIG_FOLDER = 'conf'
STAGE_WIDGETS_FOLDER = 'dist/widgets'
STAGE_TEMPLATES_FOLDER = 'dist/templates'
STAGE_USER = 'stage_user'
# created during bootstrap
STAGE_RESTORE_SCRIPT = '/opt/cloudify/stage/restore-snapshot.py'
MANAGER_PYTHON = '/opt/manager/env/bin/python'
COMPOSER_BASE_FOLDER = '/opt/cloudify-composer'
COMPOSER_CONFIG_FOLDER = 'backend/conf'
COMPOSER_BLUEPRINTS_FOLDER = 'backend/dev'

V_4_0_0 = ManagerVersion('4.0.0')
V_4_1_0 = ManagerVersion('4.1.0')
