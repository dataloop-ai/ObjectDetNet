from retinanet import AdapterModel
from dataloop_services import push_package, deploy_predict_item, create_trigger
import argparse
import dtlpy as dl
import json
import time
import logging
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--train", action='store_true', default=False)
parser.add_argument("--predict", action='store_true', default=False)
parser.add_argument("--predict_single", action='store_true', default=False)
parser.add_argument("--predict_item", action='store_true', default=False)
parser.add_argument("--deploy", action='store_true', default=False)
parser.add_argument("--trigger", action='store_true', default=False)
parser.add_argument("--new_checkpoint", action='store_true', default=False)
args = parser.parse_args()


def maybe_login():
    try:
        dl.setenv('dev')
    except:
        dl.login()
        dl.setenv('dev')


def maybe_do_deployment_stuff():
    if args.deploy:
        with open('global_configs.json', 'r') as fp:
            global_project_name = json.load(fp)['project']

        global_project = dl.projects.get(project_name=global_project_name)
        global_package_obj = push_package(global_project)
        logger.info('package pushed')
        try:
            deploy_predict_item(package=global_package_obj,
                                model_id='5e9d56bb7f6a015540d2efb4',
                                checkpoint_id='5e92e4b1e37a96cd28811a1a')
            logger.info('service deployed')
        except:
            pass
def maybe_create_trigger():
    if args.trigger:
        create_trigger()

maybe_login()
maybe_do_deployment_stuff()
maybe_create_trigger()

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
if args.new_checkpoint:
    service = dl.services.get('predict')
    model_id = '5e9d56bb7f6a015540d2efb4'
    checkpoint_id = '5e92e4b1e37a96cd28811a1a'

    model_input = dl.FunctionIO(type='Json', name='model_id', value=model_id)
    checkpoint_input = dl.FunctionIO(type='Json', name='checkpoint_id', value=checkpoint_id)
    inputs = [model_input, checkpoint_input]
    execution_obj = service.execute(execution_input=inputs, function_name='load_new_inference_checkpoint')
    while execution_obj.latest_status['status'] != 'success':
        time.sleep(5)
        execution_obj = dl.executions.get(execution_id=execution_obj.id)
        if execution_obj.latest_status['status'] == 'failed':
            raise Exception("plugin execution failed")
    logger.info("execution object status is successful")