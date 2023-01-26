resource "google_compute_network" "vpc" {
  name                    = "datapipeline-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vm_subnet" {
  name                     = "vm-subnetwork"
  ip_cidr_range            = "10.128.0.0/20"
  network                  = google_compute_network.vpc.id
  region                   = var.region
  private_ip_google_access = true
}

resource "google_compute_firewall" "internal_ingress" {
  name      = "allow-internal-ingress"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = toset(["10.128.0.0/20"])
}
