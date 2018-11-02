FROM php:7.2-apache
RUN apt-get update && apt-get install -y python3
RUN ln -s /etc/apache2/mods-available/rewrite.load /etc/apache2/mods-enabled/rewrite.load
COPY src/ /var/www/html/
CMD ["bash", "-c", "if [[ $PORT != \"\" ]]; then cd /etc/apache2; cat ports.conf | sed \"s/Listen 80/Listen $PORT/g\" > ports1.conf; mv ports1.conf ports.conf; fi; apache2-foreground"]
