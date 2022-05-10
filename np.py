'''
pip3 install kubernetes prettytable

https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NetworkPolicy.md
https://github.com/kubernetes-client/python/blob/master/kubernetes/docs/V1NetworkPolicySpec.md
https://github.com/ahmetb/kubernetes-network-policy-recipes

curl -v -XGET  -H "Accept: application/json;as=Table;v=v1;g=meta.k8s.io,application/json;as=Table;v=v1beta1;g=meta.k8s.io,application/json" -H "User-Agent: kubectl/v1.23.5 (linux/amd64) kubernetes/c285e78" 'https://192.168.49.2:8443/apis/networking.k8s.io/v1/namespaces/default/networkpolicies?limit=500'

curl -v -XGET  -H "Accept: application/json" -H "User-Agent: kubectl/v1.23.5 (linux/amd64) kubernetes/c285e78" 'https://192.168.49.2:8443/apis/networking.k8s.io/v1/namespaces/default/networkpolicies/api-allow'


'''

from prettytable import PrettyTable
from kubernetes import client, config
pt = PrettyTable()
pt.field_names = ["Policy Name", "Target_NS", "Target_POD", "Src_NS", "Src_Pod", "Src_Subnet", "Port"]


def format_dict(src):
    ret = ''
    if src:
        for k in src:
            ret = ret + k + ':' + src[k]+' '

    return ret.rstrip(" ")


def decode_netpol(name, spec):
    
    target_ns  = ""
    
    src_ns=""
    src_pod = ""
    src_subnet = ""
    port = ""
    
    #print(spec)
    if spec.ingress:
        ingress_found = 0 
        target_pod = format_dict(spec.pod_selector.match_labels)    
        for x in spec.ingress:
            ingress_found += 1
            if x.ports:
                for p in x.ports:
                    port = p.protocol+":"+ str(p.port)
            if x._from:
                for f in x._from:
            #        print(f)
                    if f.pod_selector:
                        
                        src_pod = format_dict(f.pod_selector.match_labels)
                        pt.add_row ([name, target_ns, target_pod, "", src_pod, "", port])
                    if f.namespace_selector:
                        src_ns = format_dict(f.namespace_selector.match_labels)
                        pt.add_row ([name, target_ns, target_pod, src_ns, "", "", port])
                    if f.ip_block:
                        src_subnet = f.ip_block.cidr+" Except:" +f.ip_block._except[0]
                        pt.add_row ([name, target_ns, target_pod, "", "", src_subnet, port])
    if spec.ingress == None:
        pt.add_row ([name, target_ns, "", "", "", src_subnet, port])                                
                    
    if spec.egress:
        x = 0
    
    
    

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
# v1 = client.CoreV1Api()
api_instance = client.NetworkingV1Api()

namespace = 'default'
try: 
    
    api_response  = api_instance.list_namespaced_network_policy(namespace)
    
    for x in api_response.items:
        
        name = x.metadata.name
        #print("======="+name+"========")
        decode_netpol(name, x.spec)
        

except ApiException as e:
    print("Exception when calling NetworkingV1Api->list_namespaced_network_policy: %s\n" % e)



print(pt)
