variable "region" {
  description = "La région AWS où déployer les ressources"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "Le bloc CIDR pour le VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Le bloc CIDR pour le sous-réseau public"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "Le bloc CIDR pour le sous-réseau privé"
  type        = string
  default     = "10.0.2.0/24"
}
