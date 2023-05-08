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

  source_ranges = ["10.128.0.0/20"]
}

resource "google_compute_firewall" "external_ingress" {
  name      = "allow-external-ingress"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["8080"]
  }

  source_ranges = [var.local_ip_cidr]
  target_tags   = ["airflow-webserver"]
}

resource "google_compute_firewall" "allow_http" {
  name      = "allow-http"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["80"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server"]
}

resource "google_compute_firewall" "allow_https" {
  name      = "allow-https"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["https-server"]
}

resource "google_compute_firewall" "ssh" {
  name      = "allow-ssh"
  network   = google_compute_network.vpc.name
  direction = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}
