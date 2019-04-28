<?php
  require 'params.php';  # Defines constants like FIRST
  require 'get_dilbert.php';

  if (! isset($_GET['comic']))
    $_GET['comic'] = "latest";
  $data = get_dilbert_data($_GET['comic']);
  if ($_GET['comic'] !== $data['current'])
    header('LOCATION: ' . $data['current']);
  if ($data['name'] !== "")
    $title = $data['name'] . " - ";
  else
    $title = "";
?>
<html lang="en">
  <head>
    <title><?php echo $title; ?>Dilbert Viewer</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.4.1/css/all.css" integrity="sha384-5sAR7xN1Nv6T6+dT2mhtzEpVJvfS3NScPQTrOxhwjIuvcA67KV2R5Jz6kr4abQsz" crossorigin="anonymous">
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
    <?php
      if ($data['url'] === "404")
        die("Error 404: Comic not found");
    ?>
    <div id="body" class="text-center">
      <?php
        echo '<div class="h4 mt-4">' . $data['date'] . '</div>';
        if ($data['name'] !== "")
          echo '<div class="mt-1 h6">' . $data['name'] . '</div>';
        echo '<div class="mt-4 mx-3"><img class="img-fluid" alt="' . $data['current'] . '" src="' . $data['url'] . '"></img></div><br>';

        $disable_left = ($data['current'] === FIRST) ? ' disabled' : '';
        echo '<a href="' . FIRST . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_left . '">&lt&lt</a>';
        echo '<a href="' . $data['left'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_left . '">&lt</a>';
      ?>
      <a href="random-comic" role="button" class="btn btn-primary mt-2 mx-1">Random</a>
      <?php
        $disable_right = ($data['current'] === $data['latest']) ? ' disabled' : '';
        echo '<a href="' . $data['right'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_right . '">&gt</a>';
        echo '<a href="' . $data['latest'] . '" role="button" class="btn btn-primary mt-2 mx-1 ' . $disable_right . '">&gt&gt</a>';
      ?>
      <br>
      <a href="<?php echo $data['current']; ?>" target="_blank" role="button" class="btn btn-link my-3 mx-1">Permalink</a>
      <div class="github mb-3"><a href="https://github.com/rharish101/dilbert-viewer" target="_blank" class="btn btn-light"><span class="h5"><i class="fab fa-github"></i></span></a></div>
    </div>
  </body>
</html>
