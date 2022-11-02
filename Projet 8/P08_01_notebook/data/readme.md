## Télécharger les données

sur kagle :

https://www.kaggle.com/datasets/moltean/fruits

or github :

https://github.com/Horea94/Fruit-Images-Dataset

## Comment les fruits sont filmés

https://www.youtube.com/watch?v=_HFKJ144JuU

## Commande CLI de création du cluster

```
$ aws emr create-cluster \
    --os-release-label 2.0.20220606.1 \
    --applications Name=TensorFlow Name=JupyterHub Name=Spark \
    --ec2-attributes '{"KeyName":"oc-p8_keys","InstanceProfile":"EMR_EC2_DefaultRole","SubnetId":"subnet-246b5c4d","EmrManagedSlaveSecurityGroup":"sg-0cecd6590b8913f55","EmrManagedMasterSecurityGroup":"sg-0b9f7957c5ec7b861"}' \
    --release-label emr-6.7.0 \
    --log-uri 's3n://aws-logs-945008165442-eu-west-3/elasticmapreduce/' \
    --instance-groups '[{"InstanceCount":2,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"CORE","InstanceType":"m5.xlarge","Name":"Groupe d'\''instances principal - 2"},{"InstanceCount":1,"EbsConfiguration":{"EbsBlockDeviceConfigs":[{"VolumeSpecification":{"SizeInGB":32,"VolumeType":"gp2"},"VolumesPerInstance":2}]},"InstanceGroupType":"MASTER","InstanceType":"m5.xlarge","Name":"Groupe d'\''instances maître - 1"}]' \
    --configurations '[{"Classification":"jupyter-s3-conf","Properties":{"s3.persistence.bucket":"oc-p8","s3.persistence.enabled":"true"}}]' \
    --auto-scaling-role EMR_AutoScaling_DefaultRole \
    --bootstrap-actions '[{"Path":"s3://oc-p8/emr_bootstrap.sh","Name":"Action personnalisée"}]' \
    --ebs-root-volume-size 10 \
    --service-role EMR_DefaultRole \
    --enable-debugging \
    --name 'oc-p8_cluster' \
    --scale-down-behavior TERMINATE_AT_TASK_COMPLETION \
    --region eu-west-3
```
