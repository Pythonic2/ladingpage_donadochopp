# Use uma imagem base
FROM nginx:alpine

# Copie o arquivo HTML para a imagem
COPY index.html /usr/share/nginx/html

# Exponha a porta 80
EXPOSE 82
