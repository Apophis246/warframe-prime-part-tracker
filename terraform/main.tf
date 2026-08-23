# main.tf — outline only, no implementation yet.
#
# This is where the actual OCI resources get declared. Roughly, in
# dependency order (each depends on the one above it existing):
#
#   1. provider block — configures the OCI Terraform provider (region,
#      auth). Look up: how OCI provider auth works with Terraform —
#      typically an API key you generate in the OCI console.
#   2. oci_core_vcn — the virtual network everything else lives inside
#   3. oci_core_subnet — a subnet within that VCN
#   4. oci_core_security_list — opens ports 22, 80, 443 only, per the
#      blueprint (this is what stands in for a "firewall rule" here)
#   5. oci_core_instance — the actual Ampere A1 VM. This is where
#      user_data.sh gets attached, so the VM runs it automatically on
#      first boot (look up: the instance resource's user_data /
#      metadata argument, and that it needs to be base64-encoded)
#
# Values that shouldn't be hardcoded here — compartment id, SSH key,
# instance shape/specs — belong in variables.tf instead and get
# referenced as var.<name>.
#
# Worth knowing going in (per the blueprint): Oracle's free ARM
# instances sometimes hit "out of capacity" on first apply in busy
# regions — retrying, or trying a different availability domain, is the
# usual fix. Not a sign anything here is wrong.
