#!/usr/bin/env bash
version = "latest"
docker_pull_repo="anchit2698"

docker_push_repo="anchit2698"
#docker_push_repo="164634912905.dkr.ecr.eu-west-1.amazonaws.com"

artifact="learningJenkins"
docker_reg="bjn/${artifact}"
base_image="bjn/pipeline-tfvars"
base_image_version="0.1"

docker pull ${docker_pull_repo}/${base_image}:${base_image_version}
docker tag ${docker_pull_repo}/${base_image}:${base_image_version} ${base_image}:${base_image_version}

docker build -t ${docker_reg}:{version} -t ${docker_reg}:latest -t  ${artifact}:latest -f Dockerfile .

if [[ "$#" -eq 1 ]] && [[ "$1" == 'publish' ]]; then
  docker tag ${docker_reg}:${version} ${docker_push_repo}/${docker_reg}:${version}
  docker tag ${docker_reg}:latest ${docker_push_repo}/${docker_reg}:latest
  docker push ${docker_push_repo}/${docker_reg}:${version}
fi
