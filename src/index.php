<?php
  require 'params.php';  # Defines constants like FIRST
  require 'get_dilbert.php';

  # Connect to PostgreSQL cache
  $conn = pg_connect(getenv("DATABASE_URL"));
  if (!$conn)
    die("Unable to connect to PostgreSQL");

  if (! isset($_GET['comic']))
    $_GET['comic'] = "latest";
  $data = get_dilbert_data($conn, $_GET['comic']);

  if ($_GET['comic'] !== $data['actual_date'])
    header('LOCATION: ' . $data['actual_date']);
  if ($data['title'] !== "")
    $title = $data['title'] . " - ";
  else
    $title = "";
?>
<html lang="en">
  <head>
    <title><?php echo $title; ?>Dilbert Viewer</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <link rel="icon" type="image/png" href="favicon.png" sizes="196x196">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      html, body {
        width: 100%;
        height: 100%;
      }
      html {
        display: table;
      }
      body {
        display: table-cell;
        vertical-align: middle;
      }
    </style>
  </head>
  <body>
    <div id="body" class="text-center">
      <?php
        echo '<div class="h4 mt-4">' . $data['date_str'] . '</div>';
        if ($data['title'] !== "")
          echo '<div class="mt-1 h6">' . $data['title'] . '</div>';
        echo '<div class="mt-4 mx-3"><img class="img-fluid" alt="' . $data['actual_date'] . '" src="' . $data['img_url'] . '"></img></div><br>';

        $disable_left = ($data['actual_date'] === FIRST) ? ' disabled' : '';
        echo '<a href="' . FIRST . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_left . '">&lt&lt</a>';
        echo '<a href="' . $data['left_date'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_left . '">&lt</a>';
      ?>
      <a href="random-comic" role="button" class="btn btn-primary mt-2 mx-1">Random</a>
      <?php
        $disable_right = ($data['actual_date'] === $data['latest_date']) ? ' disabled' : '';
        echo '<a href="' . $data['right_date'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_right . '">&gt</a>';
        echo '<a href="' . $data['latest_date'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_right . '">&gt&gt</a>';
      ?>
      <br>
      <a href="<?php echo 'https://dilbert.com/strip/' . $data['actual_date']; ?>" target="_blank" role="button" class="btn btn-link my-3 mx-1">Permalink</a>
      <div class="github mb-3"><a href="https://github.com/rharish101/dilbert-viewer" target="_blank" class="btn btn-light"><span class="h5"><img src="github.png" height="24" width="24"></span></a></div>
    </div>
  </body>
</html>
