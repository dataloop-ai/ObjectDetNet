from retinanet import AdapterModel
from .dataloop_services import push_package, deploy_predict_item
import argparse
import dtlpy as dl
import json

parser = argparse.ArgumentParser()
parser.add_argument("--train", action='store_true', default=False)
parser.add_argument("--predict", action='store_true', default=False)
parser.add_argument("--predict_single", action='store_true', default=False)
parser.add_argument("--predict_item", action='store_true', default=False)
parser.add_argument("--deploy_predict_item", action='store_true', default=False)
args = parser.parse_args()

def maybe_login():
    try:
        dl.setenv('prod')
    except:
        dl.login()
        dl.setenv('prod')

def maybe_do_deployment_stuff():
    if args.deploy:
        with open('global_configs.json', 'r') as fp:
            global_project_name = json.load(fp)['project']
        maybe_login()
        global_project = dl.projects.get(project_name=global_project_name)
        global_package_obj = push_package(global_project)
        try:
            predict_item_service = deploy_predict_item(package=global_package_obj)
        except:
            predict_item_service.delete()


maybe_do_deployment_stuff()

model = AdapterModel()
if args.train:
    model.load('example_checkpoint.pt')
    model.preprocess()
    model.build()
    model.train()
    model.get_checkpoint()
    model.save()
if args.predict:
    model.predict()
if args.predict_single:
    model.predict_single_image(image_path='/home/noam/0120122798.jpg')
if args.predict_item:
    project = dl.projects.get('buffs_project')
    dataset = project.datasets.get('tiny_mice_p')
    item = dataset.items.get('/items/253597.jpg')
    # filters = dl.Filters(field='filename', values='/items/253*')
    # pages = dataset.items.list(filters=filters)
    # items = [item for page in pages for item in page]
    items = [item]
    model.predict_items(items, 'checkpoint.pt')


