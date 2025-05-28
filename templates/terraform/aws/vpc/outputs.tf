output "vpc_id" {
  description = "L'ID du VPC créé"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "L'ID du sous-réseau public"
  value       = aws_subnet.public.id
}

output "private_subnet_id" {
  description = "L'ID du sous-réseau privé"
  value       = aws_subnet.private.id
}

output "internet_gateway_id" {
  description = "L'ID de la passerelle Internet"
  value       = aws_internet_gateway.gw.id
}

output "nat_gateway_id" {
  description = "L'ID de la passerelle NAT"
  value       = aws_nat_gateway.nat.id
}
