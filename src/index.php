<?php
  if (! isset($_GET['comic']))
    $_GET['comic'] = "latest";
  $command = escapeshellcmd('python3 get_dilbert.py ' . $_GET['comic']);
  $output = shell_exec($command);
  $arr = explode("\n", $output);
  $current = substr($arr[1], -10);
  if ($_GET['comic'] !== $current)
    header('LOCATION: ' . $current);
  if ($arr[7] !== "")
    $name = $arr[7] . " - ";
  else
    $name = "";
?>
<html lang="en">
  <head>
    <title><?php echo $name; ?>Dilbert Viewer</title>
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
      if ($arr[0] === "404")
        die("Error 404: Comic not found");
    ?>
    <div id="body" class="text-center">
      <?php
        echo '<div class="h4 mt-4">' . $arr[6] . '</div>';
        if ($arr[7] !== "")
          echo '<div class="mt-1 h6">' . $arr[7] . '</div>';
        echo '<div class="mt-4 mx-3"><img class="img-fluid" alt="' . $arr[1] . '" src="' . $arr[0] . '"></img></div><br>';

        if ($current === $arr[2])
        {
          echo '<a href="' . $arr[2] . '" role="button" class="btn btn-primary mt-2 mx-1 disabled" aria-disabled="true">&lt&lt</a>';
          echo '<a href="' . $arr[3] . '" role="button" class="btn btn-primary mt-2 mx-1 disabled" aria-disabled="true">&lt</a>';
        }
        else
        {
          echo '<a href="' . $arr[2] . '" role="button" class="btn btn-primary mt-2 mx-1">&lt&lt</a>';
          echo '<a href="' . $arr[3] . '" role="button" class="btn btn-primary mt-2 mx-1">&lt</a>';
        }
      ?>
      <a href="random-comic" role="button" class="btn btn-primary mt-2 mx-1">Random</a>
      <?php
        if ($current === $arr[5])
        {
          echo '<a href="' . $arr[4] . '" role="button" class="btn btn-primary mt-2 mx-1 disabled" aria-disabled="true">&gt</a>';
          echo '<a href="' . $arr[5] . '" role="button" class="btn btn-primary mt-2 mx-1 disabled" aria-disabled="true">&gt&gt</a>';
        }
        else
        {
          echo '<a href="' . $arr[4] . '" role="button" class="btn btn-primary mt-2 mx-1">&gt</a>';
          echo '<a href="' . $arr[5] . '" role="button" class="btn btn-primary mt-2 mx-1">&gt&gt</a>';
        }
      ?>
      <br>
      <a href="<?php echo $arr[1]; ?>" target="_blank" role="button" class="btn btn-link my-3 mx-1">Permalink</a>
      <div class="github mb-3"><a href="https://github.com/rharish101/dilbert-viewer" target="_blank" class="btn btn-light"><span class="h5"><i class="fab fa-github"></i></span></a></div>
    </div>
  </body>
</html>
