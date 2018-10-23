<?php
  $command = escapeshellcmd('python3 get_random_date.py');
  $output = shell_exec($command);
  $arr = explode("\n", $output);
  header('LOCATION: ' . $arr[0]);
?>
