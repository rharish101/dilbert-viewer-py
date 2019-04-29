<?php

require 'params.php';  # Defines constants like FIRST
require 'get_dilbert.php';  # Gets the comic details

# Connect to cache stored in Heroku's PostgreSQL server
$conn = pg_connect(getenv("DATABASE_URL"));
if (!$conn)
  die("Unable to connect to PostgreSQL");

# Show the latest comic by default, if nothing is requested
if (! isset($_GET['comic']))
  $_GET['comic'] = 'now';

$data = get_dilbert_data($conn, $_GET['comic']);

# Go to actual comic date
# This is useful for cases when the latest comic is requested
# In case a non-existant comic is requested, it redirects to the latest comic
if ($_GET['comic'] !== $data['actual_date'])
  header('LOCATION: ' . $data['actual_date']);

# Store stuff that is to be echoed in the HTML
$title = ($data['title'] !== "") ? ($data['title'] . ' - ') : '';  # Title of the page
$permalink = SOURCE_PREFIX . $data['actual_date'];  # Link to strip on "dilbert.com"
$disable_left = ($data['actual_date'] === FIRST) ? ' disabled' : '';  # String to disable left navigation
$disable_right = ($data['actual_date'] === $data['latest_date']) ? ' disabled' : '';  # String to disable right navigation

ob_start();
require 'static/layout.php';
ob_flush();

?>
