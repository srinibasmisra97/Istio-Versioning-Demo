import argparse
import yaml
import os
import json

BACKEND_TEMPLATES = "../k8s/backend"
FRONTEND_TEMPLATES = "../k8s/frontend"
OUTPUT_DIR = "../k8s/outputs"
NAMES_FILE = "names.txt"

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Deployment YAML Generator')

    parser.add_argument(
        '--mode',
        choices=['backend', 'frontend'],
        required=True,
        help='Generate files for Backend or Frontend'
    )

    parser.add_argument(
        '--image',
        required=True,
        help='Image path for deployment'
    )

    parser.add_argument(
        '--version',
        required=True,
        help='Version name to be used'
    )

    return parser.parse_args()

def clean_names():
    names = open(NAMES_FILE, "r").read().split("\n")

    for i in range(len(names)):
        names[i] = names[i].split("/")[1]

    return names

def filter_deployments(names, mode):
    filtered = []
    for name in names:
        if mode in name:
            filtered.append(name.split(mode + '-')[1])
    return filtered

def generate_deployment(mode, imagepath, version):
    template_dir = BACKEND_TEMPLATES if mode == "backend" else FRONTEND_TEMPLATES

    template = yaml.safe_load(open(os.path.join(template_dir, "deployment.yaml")))
    template['metadata']['name'] = mode + "-" + version
    template['metadata']['labels']['version'] = version
    template['spec']['selector']['matchLabels']['version'] = version
    template['spec']['template']['metadata']['labels']['version'] = version
    template['spec']['template']['spec']['containers'][0]['image'] = imagepath

    json.dump(template, open(os.path.join(OUTPUT_DIR, "deployment.json"), "w"))
    print("\nGENERATED DEPLOYMENT JSON")

def generate_destination_rules(mode, version, existing_deloyments):
    template_dir = BACKEND_TEMPLATES if mode == "backend" else FRONTEND_TEMPLATES

    template = yaml.safe_load(open(os.path.join(template_dir, "destinationrule.yaml")))
    rule_template = json.load(open(os.path.join(template_dir, "rule.json")))
    
    if version not in existing_deloyments:
        existing_deloyments.append(version)
    
    subsets = []
    
    for name in existing_deloyments:
        rule = rule_template
        rule['name'] = name
        rule['labels']['version'] = name
        subsets.append(rule)
    
    template['spec']['subsets'] = subsets
    json.dump(template, open(os.path.join(OUTPUT_DIR, "destinationrule.json"), "w"))
    print("\nGENERATED DESTINATION RULE JSON")

def generate_virtual_service(mode, version, existing_deloyments):
    template_dir = BACKEND_TEMPLATES if mode == "backend" else FRONTEND_TEMPLATES

    template = yaml.safe_load(open(os.path.join(template_dir, "virtualservice.yaml")))
    service_template = json.load(open(os.path.join(template_dir, "virtualservice.json")))
    
    if version not in existing_deloyments:
        existing_deloyments.append(version)
    
    for name in existing_deloyments:
        service = service_template
        service['match'][0]["headers"]["version"]["exact"] = name
        service['route'][0]['destination']['subset'] = name
        template['spec']['http'].append(service)
    
    json.dump(template, open(os.path.join(OUTPUT_DIR, "virtualservice.json"), "w"))
    print("\nGENERATED VIRTUAL SERVICE JSON")

if __name__=="__main__":
    args = parse_command_line_args()
    
    print("Existing Deployments: ")
    filtered = filter_deployments (names=clean_names(), mode=args.mode)
    for name in filtered:
        print(name)
    
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    generate_deployment(args.mode, args.image, args.version)
    generate_destination_rules(args.mode, args.version, filtered)
    generate_virtual_service(args.mode, args.version, filtered)