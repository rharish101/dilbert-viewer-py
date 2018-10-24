# Dilbert Viewer
A simple comic viewer for Dilbert by Scott Adams.  
A version without the `.htaccess` file and without caching is live [here](https://cse.iitk.ac.in/users/rharish/dilbert-viewer).

## How to Use
1. Start the docker daemon:
```
sudo systemctl start docker
```
2. Run the provided script:
```
./launch_site.sh
```
3. Kill the docker container using:
```
docker kill dilbert
```
