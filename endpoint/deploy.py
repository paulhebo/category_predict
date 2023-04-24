import json
import boto3
import traceback
import sagemaker
from sagemaker.huggingface.model import HuggingFaceModel
from datetime import datetime
import helper

sagemaker_session = sagemaker.Session()
ssmh = helper.ssm_helper()

algorithm = 'product-category'
role = ssmh.get_parameter('/industry_ai/config/meta/sagemaker_role_arn')
model_data =  ssmh.get_parameter('/industry_ai/config/meta/algorithms/{0}/artifact'.format(algorithm))
source_dir = ssmh.get_parameter('/industry_ai/config/meta/algorithms/{0}/source'.format(algorithm))

print('model_data: ', model_data)
print('source_dir: ', source_dir)
print('role: ', role)


model_name = 'product-category-model'

transformers_version = "4.6"
pytorch_version="1.7"
py_version ='py36'
entry_point = 'inference.py'

device = 'gpu'
model_environment = {"device": device}
endpoint_name = 'product-category-endpoint'

if device == 'cpu':
    instance_type = 'ml.c5.4xlarge'
else:
    instance_type = 'ml.g4dn.xlarge'

instance_count = 1

def deploy():

    model = HuggingFaceModel(
            name = model_name,
            model_data = model_data,
            entry_point = entry_point,
            source_dir = source_dir,
            role = role,
            transformers_version= transformers_version,
            pytorch_version = pytorch_version, 
            py_version = py_version,
            env = model_environment
        )
    
    predictor = model.deploy(
            endpoint_name = endpoint_name,
            instance_type = instance_type, 
            initial_instance_count = instance_count,
            async_inference_config = None,
            wait = False
        )
    
    print('Finish product-category Model Deploy initialization, Waiting Sagemaker Endpoint Creating on AWS Web Console...')

if __name__ == '__main__':
    deploy()
    print('...')




