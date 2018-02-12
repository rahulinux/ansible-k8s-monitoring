#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config

DOCUMENTATION = '''

---
module: k8s_list

short_description: Check resource exists or not 

version_added: "1.0"

description: 
    - "You can list the service, deployment, ingress and get the status of exists or not"

options:
    name: 
       description:
          - "Name of the resource"
       required: true
    namespace:
       description:
          - "namespace of the resource default: default"
       required: true
    resource:
       description:
          - "Type of resource, supported [ deployment,config_map,service,ingress,service_account,persistent_volume_claim,daemon_set ]"
       required: true

author:
  - Rahul Patil
'''

def k8s_list(data):
    has_changed = True
    config.load_kube_config()
    name = data['name']
    namespace = data['namespace']
    resource = data['resource']
    if resource in ['config_map','persistent_volume_claim','secret','service_account', 'service']:
        api = client.CoreV1Api()
        class_member = 'list_namespaced_' + resource
        action = getattr(api,class_member)
    elif resource in ['deployment', 'ingress','daemon_set']:
        extensions_v1beta1 = client.ExtensionsV1beta1Api()
        class_member = 'list_namespaced_' + resource
        action = getattr(extensions_v1beta1,class_member)
    else:
        return (False,{"msg": "not supported resource"})
    meta = { "output" : [ i.metadata.name for i in action(namespace).items if i.metadata.name == name ] }
    if len(meta['output']) == 0: 
        has_changed = False
    return (has_changed,meta)

def run_module():

    module_args = dict(
        name=dict(type='str', required=True),
        resource=dict(type='str', required=True),
        namespace=dict(type='str', required=False,default="default")
    )

    result = dict(
        ok=False,
        failed=False,
        original_message='',
        message=''
    )
    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    result['ok'],result['message'] = (k8s_list(module.params))

    if result['ok']:
        result['original_message'] = "resource {}=={} does exists".format(module.params['name'],module.params['resource']) 
    else:
        result['original_message'] = "resource {}=={} does not exists".format(module.params['name'],module.params['resource'])
        result['failed'] = True

    module.exit_json(**result) 


def main():
    run_module()

if __name__ == '__main__':
    main()
