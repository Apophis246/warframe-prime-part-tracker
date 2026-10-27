# main.tf — outline only, no implementation yet.
#
# This is where the actual OCI resources get declared. Roughly, in
# dependency order (each depends on the one above it existing):

terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 7.4"
    }
  }
}


provider "oci" {
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  private_key_path = var.private_key_path
  fingerprint      = var.fingerprint
  region           = var.region
}


data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_images" "images" {
  compartment_id = var.compartment_id
  shape          = var.instance_shape
  display_name   = "Canonical-Ubuntu-24.04-2026.09.18-0"
}


resource "oci_core_vcn" "network" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "warframe-tracker-vcn"
  dns_label      = "wftracker"
}

resource "oci_core_internet_gateway" "gateway" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.network.id
  display_name   = "intgateway"
  enabled        = true
}

resource "oci_core_route_table" "route" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.network.id
  display_name   = "route-table"
  route_rules {
    network_entity_id = oci_core_internet_gateway.gateway.id
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
  }
}

resource "oci_core_security_list" "security" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.network.id
  display_name   = "security-list"
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }
}

resource "oci_core_subnet" "subnet" {
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.network.id
  display_name      = "subnet"
  route_table_id    = oci_core_route_table.route.id
  security_list_ids = [oci_core_security_list.security.id]
  cidr_block        = "10.0.1.0/24"
  dns_label         = "public"
}

#   7. oci_core_instance — the actual Ampere A1 VM
resource "oci_core_instance" "instance" {
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  compartment_id      = var.compartment_id
  shape               = var.instance_shape
  display_name        = "instance"
  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.images.images[0].id
  }
  create_vnic_details {
    subnet_id        = oci_core_subnet.subnet.id
    assign_public_ip = true
  }
  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(file("${path.module}/user_data.sh"))
  }
}
