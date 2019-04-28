<?php

require 'params.php';
$first = new DateTime(FIRST);  # First dilbert comic ever
$now = new DateTime('now');
$span = $now->diff($first, true)->format('%d');
$days = rand(0, $span);
$rand_date = $first->add(new DateInterval('P' . $days . 'D'));
header('LOCATION: ' . $rand_date->format(FORMAT));

?>
