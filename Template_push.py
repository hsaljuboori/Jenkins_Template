import logging
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_scrapli.tasks import send_configs, send_configs_from_file
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.tasks.data import load_yaml
from nornir.core.filter import F

nr = InitNornir(config_file="config11.yaml")



def load_vars(task):
    loader = task.run(task=load_yaml, file=f"hosts_vars/{task.host}.yaml")
    group_loader = task.run(task=load_yaml, file="group_vars/all.yaml")
    task.host["facts"] = loader.result
    task.host["group_facts"] = group_loader.result


def enable_features(task):
    task.run(task=send_configs_from_file, file="baseconfig1.txt")

def vxlan_configs(task):
    template = task.run(
        task=template_file,
        template=f"{task.host['layer']}.j2",
        path="templates/vxlan",
        severity_level=logging.DEBUG,
    )
    task.host["vxlan_config"] = template.result
    rendered = task.host["vxlan_config"]
    configuration = rendered.splitlines()
    task.run(task=send_configs, configs=configuration)




filtered = nr.filter(F(layer="Leaf"))
load_vars_results = filtered.run(task=load_vars)
print_result(load_vars_results)
results = filtered.run(task=enable_features)
print_result(results)
vlxan_results = filtered.run(task=vxlan_configs)
print_result(vlxan_results)
