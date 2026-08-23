# variables.tf — outline only, no implementation yet.
#
# Declares the inputs main.tf references as var.<name>, instead of
# hardcoding them. Likely variables, based on what main.tf will need:
#
#   - compartment_id     -> which OCI compartment resources get created in
#   - region              -> which OCI region to deploy to
#   - ssh_public_key      -> for accessing the VM over SSH
#   - instance_shape      -> the Ampere A1 shape identifier
#   - instance_ocpus / instance_memory_in_gbs -> sizing within the Always
#     Free allocation (2 OCPU / 12 GB, per the blueprint — don't
#     accidentally exceed the free allocation)
#
# Each variable declaration needs a type at minimum; a description is
# good practice; a default is optional (some of these, like
# compartment_id, probably shouldn't have one — better to be forced to
# supply it than accidentally deploy to the wrong place).
#
# Where actual values go: a terraform.tfvars file (gitignored — per the
# blueprint, real values never get committed).
