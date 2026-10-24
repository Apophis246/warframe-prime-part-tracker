# main.tf — outline only, no implementation yet.
#
# This is where the actual OCI resources get declared. Roughly, in
# dependency order (each depends on the one above it existing):
#
#   0. terraform { required_providers { ... } } — declares the provider
#      source as oracle/oci. Without it, terraform init can resolve the
#      wrong namespace. Oracle's setup tutorial keeps this in a separate
#      versions.tf; the top of main.tf works just as well.
#   1. provider "oci" — API-key auth takes exactly five arguments:
#      tenancy_ocid, user_ocid, private_key_path, fingerprint, region.
#   2. oci_core_vcn — the virtual network everything else lives inside
#   3. oci_core_internet_gateway — the VCN's door to the internet
#   4. oci_core_route_table — a default route pointing at that gateway
#   5. oci_core_security_list — opens ports 22, 80, 443 only, per the
#      blueprint (this is what stands in for a "firewall rule" here)
#   6. oci_core_subnet — a subnet within the VCN, referencing the route
#      table and security list above
#   7. oci_core_instance — the actual Ampere A1 VM
#
# On 3 and 4: the blueprint's resource table omits both. That traces to
# Oracle's own compute tutorial, which creates the VCN through the
# console's Start VCN Wizard and only the instance in Terraform — the
# wizard creates an internet gateway and route table for you silently.
# Building the network here means they are yours to declare. Without
# them the VM boots, gets a public IP, and is unreachable: no SSH, no
# HTTP. Most likely way a first apply "succeeds" with a dead box.
#
# Also needed — one data source, for where to place the instance:
#   oci_identity_availability_domains, read as
#   data.oci_identity_availability_domains.<name>.availability_domains[0].name
#
# On the instance specifically:
#   - shape_config is a nested block holding ocpus and memory_in_gbs
#   - create_vnic_details needs assign_public_ip = true and the subnet_id
#   - the SSH key goes in the metadata map, under the key
#     ssh_authorized_keys. Immutable — changing it later forces the
#     instance to be replaced rather than updated in place.
#   - the image is NOT looked up by a data source in Oracle's tutorial:
#     source_type = "image", plus source_id = an image OCID copied from
#     the Image Release Notes page. Must be an ARM / aarch64 image,
#     since A1 is ARM, not x86.
#   - user_data.sh attaches through metadata as well, base64-encoded
#
# Values that shouldn't be hardcoded here — compartment id, SSH key,
# instance shape/specs — belong in variables.tf instead and get
# referenced as var.<name>.
#
# Worth knowing going in (per the blueprint): Oracle's free ARM
# instances sometimes hit "out of capacity" on first apply in busy
# regions — retrying, or trying a different availability domain, is the
# usual fix. Not a sign anything here is wrong.
