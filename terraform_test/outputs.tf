output "app_endpoint" {
  description = "The public endpoint for your Streamlit app"
  value       = azurerm_container_group.streamlit_app.ip_address
}