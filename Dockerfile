FROM php:7.2-apache
RUN apt-get update && apt-get install -y python3
RUN cp /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/
COPY src/ /var/www/html/
