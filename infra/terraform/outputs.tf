# Outputs for TaskFlow infrastructure

output "cluster_id" {
  description = "EKS cluster ID"
  value       = aws_eks_cluster.taskflow.id
}

output "cluster_arn" {
  description = "EKS cluster ARN"
  value       = aws_eks_cluster.taskflow.arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.taskflow.endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.taskflow.vpc_config[0].cluster_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.taskflow.certificate_authority[0].data
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.taskflow.name
}

output "cluster_version" {
  description = "Kubernetes version of the EKS cluster"
  value       = aws_eks_cluster.taskflow.version
}

output "node_group_arn" {
  description = "EKS node group ARN"
  value       = aws_eks_node_group.taskflow.arn
}

output "node_group_status" {
  description = "EKS node group status"
  value       = aws_eks_node_group.taskflow.status
}

output "kubectl_config_command" {
  description = "Command to configure kubectl for the EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.taskflow.name}"
}
