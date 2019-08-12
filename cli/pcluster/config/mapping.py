# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and
# limitations under the License.

from future.moves.collections import OrderedDict

from pcluster.config.params_types import (
    BoolParam,
    ClusterSection,
    DesiredSizeParam,
    EBSSettingsParam,
    EFSSection,
    IntParam,
    JsonParam,
    MaintainInitialSizeParam,
    MaxSizeParam,
    MinSizeParam,
    Section,
    SettingsParam,
    SharedDirParam,
    SpotBidPercentageParam,
    SpotPriceParam,
)

from pcluster.config.validators import (
    cluster_validator,
    compute_instance_type_validator,
    ec2_ami_validator,
    ec2_ebs_snapshot_validator,
    ec2_key_pair_validator,
    ec2_security_group_validator,
    ec2_subnet_id_validator,
    ec2_volume_validator,
    ec2_vpc_id_validator,
    efa_validator,
    efs_id_validator,
    efs_validator,
    fsx_validator,
    fsx_id_validator,
    fsx_imported_file_chunk_size_validator,
    fsx_storage_capacity_validator,
    iam_role_validator,
    placement_group_validator,
    scheduler_validator,
    raid_volume_iops_validator,
    url_validator,
)


AWS = {
    "type": Section,
    "key": "aws",
    "params": {
        "aws_access_key_id": {},
        "aws_secret_access_key": {},
        "aws_region_name": {
            "default": "us-east-1",
        },
    }
}

GLOBAL = {
    "type": Section,
    "key": "global",
    "params": {
        "cluster_template": {
            "default": "default",
        },
        "update_check": {
            "type": BoolParam,
            "default": True,
        },
        "sanity_check": {
            "type": BoolParam,
            "default": True,
        },
    }
}

ALIASES = {
    "type": Section,
    "key": "aliases",
    "params": {
        "ssh": {
            "default": "ssh {CFN_USER}@{MASTER_IP} {ARGS}"
        },
    }
}

SCALING = {
    "type": Section,
    "key": "scaling",
    "label": "default",
    "params": {
        "scaledown_idletime": {
            "type": IntParam,
            "default": 10,
            "cfn": "ScaleDownIdleTime",
        }
    }
}

VPC = {
    "type": Section,
    "key": "vpc",
    "label": "default",
    "params": {
        "vpc_id": {
            "cfn": "VPCId",
            "validator": ec2_vpc_id_validator,
        },
        "master_subnet_id": {
            "cfn": "MasterSubnetId",
            "validator": ec2_subnet_id_validator,
        },
        "ssh_from": {
            "default": "0.0.0.0/0",
            "cfn": "AccessFrom",
            #TODO "validator": cidr_validator
        },
        "additional_sg": {
            "cfn": "AdditionalSG",
            "validator": ec2_security_group_validator
        },
        "compute_subnet_id": {
            "cfn": "ComputeSubnetId",
            "validator": ec2_subnet_id_validator,
        },
        "compute_subnet_cidr": {
            "cfn": "ComputeSubnetCidr",
            # TODO "validator": cidr_validator,
        },
        "use_public_ips": {
            "type": BoolParam,
            "default": True,
            "cfn": "UsePublicIps",
        },
        "vpc_security_group_id": {
            "cfn": "VPCSecurityGroupId",
            "validator": ec2_security_group_validator
        },
    }
}

EBS = {
    "type": Section,
    "key": "ebs",
    "label": "default",
    "params": {
        "shared_dir": {
            "cfn": "SharedDir",
        },
        "ebs_snapshot_id": {
            "cfn": "EBSSnapshotId",
            "validator": ec2_ebs_snapshot_validator,
        },
        "volume_type": {
            "default": "gp2",
            "cfn": "VolumeType",
        },
        "volume_size": {
            "type": IntParam,
            "default": 20,
            "cfn": "VolumeSize",
        },
        "volume_iops": {
            "type": IntParam,
            "default": 100,
            "cfn": "VolumeIOPS",
        },
        "encrypted": {
            "type": BoolParam,
            "cfn": "EBSEncryption",
            "default": False,
        },
        "ebs_kms_key_id": {
            "cfn": "EBSKMSKeyId",
        },
        "ebs_volume_id": {
            "cfn": "EBSVolumeId",
            "validator": ec2_volume_validator,
        },
    }
}

EFS = {
    "key": "efs",
    "type": EFSSection,
    "label": "default",
    "cfn": "EFSOptions",
    "validator": efs_validator,
    "params": OrderedDict({
        "shared_dir": {},
        "efs_fs_id": {
            "validator": efs_id_validator,
        },
        "performance_mode": {
            "default": "generalPurpose",
            "allowed_values": ["generalPurpose", "maxIO"],
        },
        "efs_kms_key_id": {},
        "provisioned_throughput": {
            #"default": 1024,
            "allowed_values": "^[0-9]{1,4}(\.[0-9])?$",  # 0.0 to 1024.0
            "type": IntParam,
        },
        "encrypted": {
            "type": BoolParam,
            "default": False,
        },
        "throughput_mode": {
            "default": "bursting",
            "allowed_values": ["provisioned", "bursting"],
        },
    })
}

RAID = {
    "key": "raid",
    "label": "default",
    "type": Section,
    "cfn": "RAIDOptions",
    "params":  OrderedDict({
        "shared_dir": {
        },
        "raid_type": {
            "type": IntParam,
            "allowed_values": [0, 1],
        },
        "num_of_raid_volumes": {
            "type": IntParam,
            "allowed_values": "^[1-5]$"
        },
        "volume_type": {
            "default": "gp2",
            "cfn": "VolumeType",
        },
        "volume_size": {
            "type": IntParam,
            "default": 20,
            "cfn": "VolumeSize",
        },
        "volume_iops": {
            "type": IntParam,
            "default": 100,
            "cfn": "VolumeIOPS",
            "validator": raid_volume_iops_validator
        },
        "encrypted": {
            "type": BoolParam,
            "default": False,
            "cfn": "EBSEncryption",
        },
        "ebs_kms_key_id": {
            "cfn": "EBSKMSKeyId",
        },
    })
}


FSX = {
    "key": "fsx",
    "label": "default",
    "type": Section,
    "validator": fsx_validator,
    "cfn": "FSXOptions",
    "params": OrderedDict({
        "shared_dir": {},
        "fsx_fs_id": {
            "validator": fsx_id_validator,
        },
        "storage_capacity": {
            "type": IntParam,
            "validator": fsx_storage_capacity_validator
        },
        "fsx_kms_key_id": {},
        "imported_file_chunk_size": {
            "type": IntParam,
            "validator": fsx_imported_file_chunk_size_validator
        },
        "export_path": {},
        "import_path": {},
        "weekly_maintenance_start_time": {},
    })
}

CLUSTER = {
    "key": "cluster",
    "label": "default",
    "type": ClusterSection,
    "validator": cluster_validator,
    "params": {
        # Basic configuration
        "key_name": {
            "cfn": "KeyName",
            "validator": ec2_key_pair_validator,
        },
        "template_url": {
            "validator": url_validator,
        },
        "base_os": {
            "default": "alinux",
            "cfn": "BaseOS",
            "allowed_values": ["alinux", "ubuntu1404", "ubuntu1604", "centos6", "centos7"],
        },
        "scheduler": {
            "default": "sge",
            "cfn": "Scheduler",
            "allowed_values": ["awsbatch", "sge", "slurm", "torque"],
            "validator": scheduler_validator,
        },
        "shared_dir": {
            "type": SharedDirParam,
            "cfn": "SharedDir",
            "default": "/shared",
            "validator": None,  # TODO
        },
        # Cluster configuration
        "placement_group": {
            "cfn": "PlacementGroup",
            "validator": placement_group_validator,
        },
        "placement": {
            "default": "compute",
            "cfn": "Placement",
            "allowed_values": ["cluster", "compute"],
        },
        # Master
        "master_instance_type": {
            "default": "t2.micro",
            "cfn": "MasterInstanceType",
            "validator": None,
        },
        "master_root_volume_size": {
            "type": IntParam,
            "default": 17,
            "cfn": "MasterRootVolumeSize",
        },
        # Compute fleet
        "compute_instance_type": {
            "default": "t2.micro",
            "cfn": "ComputeInstanceType",
            "validator": compute_instance_type_validator,
        },
        "compute_root_volume_size": {
            "type": IntParam,
            "default": 17,
            "cfn": "ComputeRootVolumeSize",
        },
        "initial_queue_size": {
            "type": DesiredSizeParam,
            "default": 0,
            "cfn": "DesiredSize",  # FIXME verify the update case
        },
        "max_queue_size": {
            "type": MaxSizeParam,
            "default": 10,
            "cfn": "MaxSize",
            "validator": None,  # TODO we could test the account capacity
        },
        "maintain_initial_size": {
            "type": MaintainInitialSizeParam,
            "default": False,
        },
        "min_vcpus": {
            "type": MinSizeParam,
            "default": 0,
            "cfn": "MinSize",
        },
        "desired_vcpus": {
            "type": DesiredSizeParam,
            "default": 2,
            "cfn": "DesiredSize",
        },
        "max_vcpus": {
            "type": MaxSizeParam,
            "default": 10,
            "cfn": "MaxSize",
        },
        "cluster_type": {
            "default": "ondemand",
            "allowed_values": ["ondemand", "spot"],
            "cfn": "ClusterType",
        },
        "spot_price": {
            "type": SpotPriceParam,
            "default": 10,
            "cfn": "SpotPrice",
        },
        "spot_bid_percentage": {
            "type": SpotBidPercentageParam,
            "default": 0.00,
            "cfn": "SpotPrice",
        },
        # Access and networking
        "proxy_server": {
            "cfn": "ProxyServer",
        },
        "ec2_iam_role": {
            "cfn": "EC2IAMRoleName",
            "validator": iam_role_validator,
        },
        "s3_read_resource": {
            "cfn": "S3ReadResource",
        },
        "s3_read_write_resource": {
            "cfn": "S3ReadWriteResource",
        },
        # Customization
        "enable_efa": {
            "allowed_values": ["compute"],
            "cfn": "EFA",
            "validator": efa_validator,
        },
        "ephemeral_dir": {
            "default": "/scratch",
            "cfn": "EphemeralDir",
        },
        "encrypted_ephemeral": {
            "default": False,
            "type": BoolParam,
            "cfn": "EncryptedEphemeral",
        },
        "custom_ami": {
            "cfn": "CustomAMI",
            "validator": ec2_ami_validator,
        },
        "pre_install": {
            "cfn": "PreInstallScript",
            "validator": url_validator,
        },
        "pre_install_args": {
            "cfn": "PreInstallArgs",
        },
        "post_install": {
            "cfn": "PostInstallScript",
            "validator": url_validator,
        },
        "post_install_args": {
            "cfn": "PostInstallArgs",
        },
        "extra_json": {
            "type": JsonParam,
            "cfn": "ExtraJson",
        },
        "additional_cfn_template": {
            "validator": url_validator,
            "cfn": "AdditionalCfnTemplate",
        },
        "tags": {
            "type": JsonParam,
        },
        "custom_chef_cookbook": {
            "cfn": "CustomChefCookbook",
        },
        "custom_awsbatch_template_url": {
            "cfn": "CustomAWSBatchTemplateURL",
            "validator": url_validator,
        },
        # Settings
        "scaling_settings": {
            "type": SettingsParam,
            "referred_section": SCALING,
        },
        "vpc_settings": {
            "type": SettingsParam,
            "referred_section": VPC,
        },
        "ebs_settings": {
            "type": EBSSettingsParam,
            "referred_section": EBS,
        },
        "efs_settings": {
            "type": SettingsParam,
            "referred_section": EFS,
        },
        "raid_settings": {
            "type": SettingsParam,
            "referred_section": RAID,
        },
        "fsx_settings": {
            "type": SettingsParam,
            "referred_section": FSX,
        },
    }
}

MAIN_SECTIONS = [AWS, GLOBAL, CLUSTER, ALIASES]