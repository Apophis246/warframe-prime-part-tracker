# variables.tf — declares the inputs main.tf references as var.<name>,
# instead of hardcoding them.
#
# Provider auth — the oci provider takes exactly these five for API-key
# auth. Values come from ~/.oci/config, or the console under
# Profile -> User settings -> API keys -> Actions -> View configuration file:
#
#   - tenancy_ocid        -> the config's tenancy=
#   - user_ocid           -> user=
#   - fingerprint         -> fingerprint=
#   - private_key_path    -> key_file=  (mark sensitive = true. The console
#                            preview's value is a placeholder — supply the
#                            real path to the .pem yourself.)
#   - region              -> region=
#
# Resource inputs:
#
#   - compartment_id     -> which OCI compartment resources get created in
#   - ssh_public_key      -> the .pub file's CONTENTS pasted as a string,
#                            for accessing the VM over SSH (not a path —
#                            main.tf uses it directly, no file() call)
#   - instance_shape      -> the Ampere A1 shape identifier
#   - instance_ocpus / instance_memory_in_gbs -> sizing within the Always
#     Free allocation (2 OCPU / 12 GB, per the blueprint — don't
#     accidentally exceed the free allocation)
#
# Each variable declaration needs a type at minimum; a description is
# good practice; a default is optional.
#
# Where actual values go: this file is tracked in git, *.tfvars is not.
# So anything account-specific — the OCIDs, fingerprint, key path, ssh
# key — goes in terraform.tfvars, NOT as a default here. Defaults are
# fine for shape / ocpus / memory, which aren't account-specific.


variable "tenancy_ocid" {
  type        = string
  description = "OCID of the tenancy (root compartment); used for API auth"
}

variable "user_ocid" {
  type        = string
  description = "OCID of the user whose API key signs requests"
}

variable "fingerprint" {
  type        = string
  description = "Fingerprint of the API signing key uploaded to OCI"
}

variable "private_key_path" {
  type        = string
  description = "Absolute path to the API signing private key (.pem)"
  sensitive   = true
}

variable "region" {
  type        = string
  description = "OCI region identifier to deploy into, e.g. us-sanjose-1"
}

variable "compartment_id" {
  type        = string
  description = "OCID of the compartment all resources are created in"
}

variable "ssh_public_key" {
  type        = string
  description = "SSH public key text installed on the VM for login"
}

variable "instance_shape" {
  type        = string
  description = "Compute shape; E2.1.Micro is the x86 Always Free shape"
  default     = "VM.Standard.E2.1.Micro"
}

variable "instance_ocpus" {
  type        = number
  description = "OCPUs; unused on E2.1.Micro (fixed shape). Needed only if switching back to A1.Flex, where 2 is the Always Free maximum"
  default     = 1
}

variable "instance_memory_in_gbs" {
  type        = number
  description = "Memory in GB; unused on E2.1.Micro (fixed shape). Needed only if switching back to A1.Flex, where 12 is the Always Free maximum"
  default     = 6
}