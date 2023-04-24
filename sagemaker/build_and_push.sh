if [ "$#" -gt 3 -o "$#" -lt 2 ]; then
    echo "usage: $0 [s3uri] [region] [algorithm]"
    exit 1
fi

s3uri=$1
region=$2
algorithm=$3

sagemaker_dir="$PWD"

if [ ! -z "$algorithm" ]; then
    dirlist=${algorithm}
else
    dirlist=$(find . -mindepth 1 -maxdepth 1 -type d)
fi

echo $dirlist
cd ${sagemaker_dir}/${dirlist}
echo ${sagemaker_dir}/${dirlist}

tar czvf sourcedir.tar.gz *
aws s3 cp sourcedir.tar.gz ${s3uri}/algorithms/${algorithm}/source/ --region ${region}
rm sourcedir.tar.gz

cd ${sagemaker_dir}/model
echo ${sagemaker_dir}/model
aws s3 cp model.tar.gz ${s3uri}/algorithms/${algorithm}/artifact/ --region ${region}