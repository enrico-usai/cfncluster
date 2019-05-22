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

from enum import Enum

from pcluster.config.param_types import (
    AdditionalIamPoliciesParam,
    AvailabilityZoneParam,
    BoolParam,
    ClusterSection,
    DesiredSizeParam,
    EBSSettingsParam,
    EFSSection,
    FloatParam,
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
    ec2_iam_policies_validator,
    ec2_iam_role_validator,
    ec2_key_pair_validator,
    ec2_placement_group_validator,
    ec2_security_group_validator,
    ec2_subnet_id_validator,
    ec2_volume_validator,
    ec2_vpc_id_validator,
    efa_validator,
    efs_id_validator,
    efs_validator,
    fsx_id_validator,
    fsx_imported_file_chunk_size_validator,
    fsx_storage_capacity_validator,
    fsx_validator,
    raid_volume_iops_validator,
    scheduler_validator,
    url_validator,
)


class CommonRegex(Enum):
    """Utility class containing all the common regex used in the section mapping."""

    CIDR = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/(0|1[6-9]|2[0-9]|3[0-2])$"
    SECURITY_GROUP_ID = r"^sg-[0-9a-z]{8}$|^sg-[0-9a-z]{17}$"
    SUBNET_ID = r"^subnet-[0-9a-z]{8}$|^subnet-[0-9a-z]{17}$"


AWS = {
    "type": Section,
    "key": "aws",
    "params": {
        "aws_access_key_id": {},
        "aws_secret_access_key": {},
        "aws_region_name": {
            "default": "us-east-1",  # TODO add regex
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
            "allowed_values": r"^vpc-[0-9a-z]{8}$|^vpc-[0-9a-z]{17}$",
            "validator": ec2_vpc_id_validator,
        },
        "master_subnet_id": {
            "cfn": "MasterSubnetId",
            "allowed_values": CommonRegex.SUBNET_ID.value,
            "validator": ec2_subnet_id_validator,
        },
        "ssh_from": {
            "default": "0.0.0.0/0",
            "allowed_values": CommonRegex.CIDR.value,
            "cfn": "AccessFrom",
        },
        "additional_sg": {
            "cfn": "AdditionalSG",
            "allowed_values": CommonRegex.SECURITY_GROUP_ID.value,
            "validator": ec2_security_group_validator,
        },
        "compute_subnet_id": {
            "cfn": "ComputeSubnetId",
            "allowed_values": CommonRegex.SUBNET_ID.value,
            "validator": ec2_subnet_id_validator,
        },
        "compute_subnet_cidr": {
            "cfn": "ComputeSubnetCidr",
            "allowed_values": CommonRegex.CIDR.value,
        },
        "use_public_ips": {
            "type": BoolParam,
            "default": True,
            "cfn": "UsePublicIps",
        },
        "vpc_security_group_id": {
            "cfn": "VPCSecurityGroupId",
            "allowed_values": CommonRegex.SECURITY_GROUP_ID.value,
            "validator": ec2_security_group_validator,
        },
        "master_availability_zone": {
            # NOTE: this is not exposed as a configuration parameter
            "type": AvailabilityZoneParam,
            "cfn": "AvailabilityZone",
        }
    },
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
            "allowed_values": r"^snap-[0-9a-z]{8}$|^snap-[0-9a-z]{17}$",
            "cfn": "EBSSnapshotId",
            "validator": ec2_ebs_snapshot_validator,
        },
        "volume_type": {
            "default": "gp2",
            "allowed_values": ["standard", "io1", "gp2", "st1", "sc1"],
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
            "allowed_values": r"^vol-[0-9a-z]{8}$|^vol-[0-9a-z]{17}$",
            "validator": ec2_volume_validator,
        },
    },
}

EFS = {
    "key": "efs",
    "type": EFSSection,
    "label": "default",
    "validator": efs_validator,
    "cfn": "EFSOptions",  # All the parameters in the section are converted into a single CFN parameter
    "params": OrderedDict(  # Use OrderedDict because the parameters must respect the order in the CFN parameter
        [
            ("shared_dir", {}),
            ("efs_fs_id", {
                "allowed_values": r"^fs-[0-9a-z]{8}$|^fs-[0-9a-z]{17}|NONE$",
                "validator": efs_id_validator,
            }),
            ("performance_mode", {
                "default": "generalPurpose",
                "allowed_values": ["generalPurpose", "maxIO"],
            }),
            ("efs_kms_key_id", {}),
            ("provisioned_throughput", {
                "allowed_values": r"^([0-9]{1,3}|10[0-1][0-9]|102[0-4])(\.[0-9])?$",  # 0.0 to 1024.0
                "type": FloatParam,
            }),
            ("encrypted", {
                "type": BoolParam,
                "default": False,
            }),
            ("throughput_mode", {
                "default": "bursting",
                "allowed_values": ["provisioned", "bursting"],
            }),
        ]
    )
}

RAID = {
    "type": Section,
    "key": "raid",
    "label": "default",
    "cfn": "RAIDOptions",  # All the parameters in the section are converted into a single CFN parameter
    "params": OrderedDict(  # Use OrderedDict because the parameters must respect the order in the CFN parameter
        [
            ("shared_dir", {}),
            ("raid_type", {
                "type": IntParam,
                "allowed_values": [0, 1],
            }),
            ("num_of_raid_volumes", {
                "type": IntParam,
                "allowed_values": "^[1-5]$",
            }),
            ("volume_type", {
                "default": "gp2",
                "allowed_values": ["standard", "io1", "gp2", "st1", "sc1"],
            }),
            ("volume_size", {
                "type": IntParam,
                "default": 20,
            }),
            ("volume_iops", {
                "type": IntParam,
                "default": 100,
                "validator": raid_volume_iops_validator,
            }),
            ("encrypted", {
                "type": BoolParam,
                "default": False,
            }),
            ("ebs_kms_key_id", {}),
        ]
    )
}


FSX = {
    "type": Section,
    "key": "fsx",
    "label": "default",
    "validator": fsx_validator,
    "cfn": "FSXOptions",  # All the parameters in the section are converted into a single CFN parameter
    "params": OrderedDict(  # Use OrderedDict because the parameters must respect the order in the CFN parameter
        [
            ("shared_dir", {}),
            ("fsx_fs_id", {
                "allowed_values": r"^fs-[0-9a-z]{17}|NONE$",
                "validator": fsx_id_validator,
            }),
            ("storage_capacity", {
                "type": IntParam,
                "validator": fsx_storage_capacity_validator
            }),
            ("fsx_kms_key_id", {}),
            ("imported_file_chunk_size", {
                "type": IntParam,
                "validator": fsx_imported_file_chunk_size_validator
            }),
            ("export_path", {}),  # TODO add regex
            ("import_path", {}),  # TODO add regex
            ("weekly_maintenance_start_time", {}),  # TODO add regex
        ]
    )
}

CLUSTER = {
    "type": ClusterSection,
    "key": "cluster",
    "label": "default",
    "validator": cluster_validator,
    "params": {
        # Basic configuration
        "key_name": {
            "cfn": "KeyName",
            "validator": ec2_key_pair_validator,
        },
        "template_url": {
            # TODO add regex
            "validator": url_validator,
        },
        "base_os": {
            "default": "alinux",
            "cfn": "BaseOS",
            "allowed_values": ["alinux", "ubuntu1604", "ubuntu1804", "centos6", "centos7"],
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
        },
        # Cluster configuration
        "placement_group": {
            "cfn": "PlacementGroup",
            "validator": ec2_placement_group_validator,
        },
        "placement": {
            "default": "compute",
            "cfn": "Placement",
            "allowed_values": ["cluster", "compute"],
        },
        # Master
        "master_instance_type": {
            "default": "t2.micro",  # TODO add regex or validator
            "cfn": "MasterInstanceType",
        },
        "master_root_volume_size": {
            "type": IntParam,
            "default": 20,
            "allowed_values": r"^([0-9]+[0-9]{2}|[2-9][0-9])$",  # >= 20
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
            "default": 20,
            "allowed_values": r"^([0-9]+[0-9]{2}|[2-9][0-9])$",  # >= 20
            "cfn": "ComputeRootVolumeSize",
        },
        "initial_queue_size": {
            "type": DesiredSizeParam,
            "default": 0,
            "cfn": "DesiredSize",  # TODO verify the update case
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
            "cfn": "MinSize",
        },
        "min_vcpus": {
            "type": MinSizeParam,
            "default": 0,
            "cfn": "MinSize",
        },
        "desired_vcpus": {
            "type": DesiredSizeParam,
            "default": 4,
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
            "default": 0.0,
            "cfn": "SpotPrice",
        },
        "spot_bid_percentage": {
            "type": SpotBidPercentageParam,
            "default": 0,
            "cfn": "SpotPrice",
            "allowed_values": r"^(100|[1-9][0-9]|[0-9])$",  # 0 <= value <= 100
        },
        # Access and networking
        "proxy_server": {
            "cfn": "ProxyServer",
        },
        "ec2_iam_role": {
            "cfn": "EC2IAMRoleName",
            "validator": ec2_iam_role_validator,  # TODO add regex
        },
        "additional_iam_policies": {
            "type": AdditionalIamPoliciesParam,
            "cfn": "EC2IAMPolicies",
            "validator": ec2_iam_policies_validator,
        },
        "s3_read_resource": {
            "cfn": "S3ReadResource",  # TODO add validator
        },
        "s3_read_write_resource": {
            "cfn": "S3ReadWriteResource",  # TODO add validator
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
            "allowed_values": r"^ami-[0-9a-z]{8}$|^ami-[0-9a-z]{17}$",
            "validator": ec2_ami_validator,
        },
        "pre_install": {
            "cfn": "PreInstallScript",
            # TODO add regex
            "validator": url_validator,
        },
        "pre_install_args": {
            "cfn": "PreInstallArgs",
        },
        "post_install": {
            "cfn": "PostInstallScript",
            # TODO add regex
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
            "cfn": "AdditionalCfnTemplate",
            # TODO add regex
            "validator": url_validator,
        },
        "tags": {
            "type": JsonParam,
        },
        "custom_chef_cookbook": {
            "cfn": "CustomChefCookbook",
            # TODO add regex
            "validator": url_validator,
        },
        "custom_awsbatch_template_url": {
            "cfn": "CustomAWSBatchTemplateURL",
            # TODO add regex
            "validator": url_validator,
        },
        # Settings
        "scaling_settings": {
            "type": SettingsParam,
            "default": "default",  # set a value to create always the internal structure for the scaling section
            "referred_section": SCALING,
        },
        "vpc_settings": {
            "type": SettingsParam,
            "default": "default",  # set a value to create always the internal structure for the vpc section
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

GLOBAL = {
    "type": Section,
    "key": "global",
    "params": {
        "cluster_template": {
            # TODO This could be a SettingsParam referring to a CLUSTER section
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
