#!/bin/bash
set -v
set -e
#

# This script should be run from the repo's backend directory
#
#
# Get s3uri and region from command line
s3uri=$1
region=$2

# Get reference for all important folders
backend_dir="$PWD"
project_dir="$backend_dir/.."
build_dist_dir="$backend_dir/build/codes"
source_dir="$backend_dir/src"
build_dir="$backend_dir/build/tmp"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist, node_modules and bower_components folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

mkdir -p ${build_dir}/


echo "------------------------------------------------------------------------------"
echo "[Rebuild] industry_ai_sagemaker lambda functions"
echo "------------------------------------------------------------------------------"

echo ${source_dir}
cd ${source_dir}/industry_ai_sagemaker
rm -r ${build_dir}

mkdir -p ${build_dir}/python/

cp -R * ${build_dir}/python/
cd ${build_dir}
zip -r9 industry_ai_sagemaker.zip python
cp ${build_dir}/industry_ai_sagemaker.zip $build_dist_dir/industry_ai_sagemaker.zip
rm ${build_dir}/industry_ai_sagemaker.zip


echo "------------------------------------------------------------------------------"
echo "[Rebuild] industry_ai_helper lambda functions"
echo "------------------------------------------------------------------------------"

echo ${source_dir}
cd ${source_dir}/industry_ai_helper
rm -r ${build_dir}

mkdir -p ${build_dir}/python/

cp -R *.py ${build_dir}/python/
cd ${build_dir}
zip -r9 industry_ai_helper.zip python
cp ${build_dir}/industry_ai_helper.zip $build_dist_dir/industry_ai_helper.zip
rm ${build_dir}/industry_ai_helper.zip

echo "------------------------------------------------------------------------------"
echo "[Rebuild] other industry_ai_* lambda functions"
echo "------------------------------------------------------------------------------"


lambda_foldes="
industry_ai_inference
industry_ai_invoke_endpoint
"

for lambda_folder in $lambda_foldes; do
    # build and copy console distribution files
    echo ${source_dir}
    cd ${source_dir}/${lambda_folder}
    echo ${build_dir}
    rm -r ${build_dir}

    mkdir -p ${build_dir}/
    cp -R * ${build_dir}/
    cd ${build_dir}
    zip -r9 ${lambda_folder}.zip .
    cp ${build_dir}/${lambda_folder}.zip $build_dist_dir/${lambda_folder}.zip
    rm ${build_dir}/${lambda_folder}.zip
done

aws s3 cp ${project_dir}/backend/build/codes ${s3uri}/codes --recursive --region ${region}
#aws s3 cp ${project_dir}/backend/assets/greengrass  ${s3uri}/algorithms/yolov5/greengrass/ --recursive --region ${region}

echo "All Done!"
