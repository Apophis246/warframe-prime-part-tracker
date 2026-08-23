# outputs.tf — outline only, no implementation yet.
#
# Per the blueprint: the VM's public IP, printed after `terraform
# apply`. Look up: the output block syntax, and which attribute on the
# oci_core_instance resource actually holds the public IP (it may
# require a separate oci_core_vnic_attachment / data source lookup,
# depending on how you provision it — worth checking OCI's Terraform
# provider docs when you get here rather than guessing).
