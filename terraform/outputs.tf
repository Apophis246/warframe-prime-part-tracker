# outputs.tf — outline only, no implementation yet.
#
# Per the blueprint: the VM's public IP, printed after `terraform
# apply`. One output block is all this needs.
#
# Resolved — no separate oci_core_vnic_attachment resource or data
# source lookup is required. The attribute lives directly on the
# instance:
#
#   oci_core_instance.<name>.public_ip
#
# Look up: the output block syntax itself (value, description).
