FROM php:7.2-apache
RUN apt-get update && apt-get install -y python3
RUN ln -s /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
COPY src/ /var/www/html/
