import argparse
import yaml
import os
import json

BACKEND_TEMPLATES = "./k8s/backend"
FRONTEND_TEMPLATES = "./k8s/frontend"
OUTPUT_DIR = "./k8s/outputs"
NAMES_FILE = "./generator/names.txt"

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

    names = [name for name in names if name != '']

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

    yaml.dump(template, open(os.path.join(OUTPUT_DIR, "deployment.yaml"), "w"))
    print("\nGENERATED DEPLOYMENT YAML")

def generate_destination_rules(mode, version, existing_deloyments):
    template_dir = BACKEND_TEMPLATES if mode == "backend" else FRONTEND_TEMPLATES

    template = yaml.safe_load(open(os.path.join(template_dir, "destinationrule.yaml")))
    
    if version not in existing_deloyments:
        existing_deloyments.append(version)
    
    subsets = []
    
    for name in existing_deloyments:
        subsets.append({
            "name": name,
            "labels": {
                "version": name
            }
        })

    template['spec']['subsets'] = subsets
    yaml.dump(template, open(os.path.join(OUTPUT_DIR, "destinationrule.yaml"), "w"))
    print("\nGENERATED DESTINATION RULE YAML")

def generate_virtual_service(mode, version, existing_deloyments):
    template_dir = BACKEND_TEMPLATES if mode == "backend" else FRONTEND_TEMPLATES

    template = yaml.safe_load(open(os.path.join(template_dir, "virtualservice.yaml")))
    
    if version not in existing_deloyments:
        existing_deloyments.append(version)
    
    temp = []
    for name in existing_deloyments:
        temp.append({
            "match": [
                {
                "headers": {
                    "version": {
                    "exact" : name
                    }
                }
                }
            ],
            "route": [
                {
                "destination": {
                    "host": "backend",
                    "subset": name,
                    "port": {
                    "number": 5000
                    }
                }
                }
            ]
        })
    
    temp.append(template['spec']['http'][0])
    template['spec']['http'] = temp
    yaml.dump(template, open(os.path.join(OUTPUT_DIR, "virtualservice.yaml"), "w"))
    print("\nGENERATED VIRTUAL SERVICE YAML")

if __name__=="__main__":
    args = parse_command_line_args()
    
    filtered = filter_deployments (names=clean_names(), mode=args.mode)
    
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    if args.mode in args.version:
        names = args.version.split("/")
        args.version = names[len(names) - 1]

    generate_deployment(args.mode, args.image, args.version)
    generate_destination_rules(args.mode, args.version, filtered)
    generate_virtual_service(args.mode, args.version, filtered)