#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from kubernetes import client, config
import kubernetes
import json

class CustomResource(object):
    def __init__(self):
        config = client.Configuration()
        if not config.api_client:
            config.api_client = client.ApiClient()
        self.api_client = config.api_client

    def run(self, body, namespace='default', domain=None,api_version=None,kind=None):
        resource_path = '/apis/' + domain + '/' + api_version +  '/namespaces/' +  namespace + '/' + kind
        header_params = {}
        header_params['Accept'] = self.api_client.select_header_accept(['application/json'])
        header_params['Content-Type'] = self.api_client.select_header_content_type(['*/*'])

        (resp, code, header) = self.api_client.call_api(
               resource_path, 'GET', { 'namespace': namespace}, {}, header_params, body, [], _preload_content=False)

        data =  json.loads(resp.data.decode('utf-8'))

        if body.get('state') == 'present':
           # Check if already exists
           for i in data['items']:
              if i['metadata']['name'] == body['metadata']['name']:
                 header_params['Content-Type'] = self.api_client.select_header_content_type(['application/merge-patch+json'])
                 resource_path = i['metadata']['selfLink']
                 (resp, code, header) = self.api_client.call_api(
                   resource_path, 'PATCH', { 'name': 'prometheus', 'namespace': namespace }, {}, header_params, body, [], _preload_content=True)
                 if code == 200:
                    return json.dumps(dict(status="Successfully Updated"))
                 return json.dumps(dict(status="Something wrong with patch object"))
           else:
              (resp, code, header) = self.api_client.call_api(
                   resource_path, 'POST', { 'namespace': namespace}, {}, header_params, body, [], _preload_content=False)
              if code == 201:
                 return json.dumps(dict(status="Successfully added"))
              return json.dumps(dict(status="Something went wrong with add object"))

        elif body.get('state') == 'absent':
           body['kind'] = 'DeleteOptions'
           (resp, code, header) = self.api_client.call_api(
                   resource_path, 'DELETE', {'namespace': namespace}, {}, header_params, body, [], _preload_content=False)
           data = json.loads(resp.data.decode('utf-8'))
           if  data['items'] == []:
                 return json.dumps(dict(status="Already deleted"))
           return json.dumps(dict(status="Successfully Deleted"))

        return json.loads(resp.data.decode('utf-8'))


def k8s_prometheus(data):
    config.load_kube_config()
    data['metadata'] = { 'name': data.get('name'),
                         'namespace': data.get('namespace'),
                         'labels': data.get('labels') }
    del data['labels']
    del data['namespace']
    api = CustomResource()
    kinds = { 'ServiceMonitor' : 'servicemonitors',
              'Prometheus': 'prometheuses',
              'Alertmanager': 'alertmanagers' }
    api_response = api.run(body=data,domain='monitoring.coreos.com',
            api_version='v1',kind=kinds.get(data.get('kind')),namespace='monitoring') 
    if 'Success' in api_response:
          return (True,api_response)
    return (False,api_response)



def run_module():

    module_args = dict(
            name=dict(type='str',required=True),
            namespace=dict(type='str',required=True),
            spec=dict(type='dict',required=False),
            labels=dict(type='dict',required=False),
            state=dict(type='str',required=False,default='present'),
            apiVersion=dict(type='str',required=False,default='monitoring.coreos.com/v1'),
            kind=dict(type='str',required=True)
    )

    result = dict(
        changed=False,
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result

    result['changed'],result['message'] = (k8s_prometheus(module.params))

    module.exit_json(**result) 

def main():
    run_module()

if __name__ == '__main__':
    main()
