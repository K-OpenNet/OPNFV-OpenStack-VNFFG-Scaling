#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
from oslo_config import cfg
from oslo_log import log as logging

from tacker.plugins.common import constants
from tacker.vnfm.policy_actions import abstract_action
from tacker.vnfm import utils as vnfm_utils
from tacker import manager
from tacker.common import rpc
from tacker.common import topics

LOG = logging.getLogger(__name__)


class VNFActionNotify(abstract_action.AbstractPolicyAction):
    def get_type(self):
        return 'notify'

    def get_name(self):
        return 'notify'

    def get_description(self):
        return 'Tacker VNF notify policy'

    # Should define the below action
    # When event ocurrs, VNFM only notify event with related infromation  (e.g., vnf_id) to NFVO
    # Then, NFVO finds VNFFG which include the VNF and decides wether VNFFG should be deleted or changed.
    def execute_action(self, plugin, context, vnf_dict, args):
        vnf_old_id = vnf_dict['id']
        LOG.info('log : args is %s', args)
        #LOG.info('log : dir(vnf_dict) is %s', dir(vnf_dict))
        #LOG.info('log : vnf_dict.values() is %s', vnf_dict.values())
        #LOG.info('log : dir(context.session) is %s', dir(context.session))
        #LOG.info('log : dir(vnf_dict) is %s', dir(vnf_dict))
        LOG.info('log : vnf %s is dead and needs to be respawned', vnf_old_id)
        nfvo_plugin = manager.TackerManager.get_service_plugins()['NFVO']
        LOG.info('NFVO_plugin is called')
        
        #To defined Check VNFFG
#        vnf_new_id = vnf_old_id
#        nfvo_plugin.mark_event(context, vnf_old_id,vnf_new_id)

        def start_rpc_listners():
            self.endpoints = [self]
            self.connection = rpc.create_connection()
            LOG.info('log: self.connection = %s', self.connection) ###
            self.connection.create_consumer(topics.TOPIC_ACTION_KILL,
                                            self.endpoints, fanout=False,
                                            host=vnf_old_id)
            LOG.info('log: create_consumer completed') ###
            return self.connection.consume_in_threads()

        try:
            rpc.init_action_rpc(cfg.CONF) ###
            LOG.info('log: dir(cfg.CONF) = %s', dir(cfg.CONF)) ###
            servers = self.start_rpc_listeners()

        except Exception:
            LOG.exception('failed to start rpc')
            return 'FAILED'

        

