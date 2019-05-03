<!DOCTYPE HTML>
<html lang="en">

<head>
  <title><?php echo $title; ?>Dilbert Viewer</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
  <link rel="stylesheet" href="static/styles.css">
  <link rel="icon" type="image/png" href="static/resources/favicon.png" sizes="96x96">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body>
  <div id="body" class="text-center">

  <!-- Date and title (if exists) -->
  <div class="h4 mt-4"><?php echo $data['date_str']; ?></div>
  <div class="mt-1 h6"><?php echo $data['title']; ?></div>

  <!-- Comic image -->
  <div class="mt-4 mx-3"><img class="img-fluid" alt="<?php echo $data['actual_date']; ?>" src="<?php echo $data['img_url']; ?>"></img></div>
  <br>

  <!-- Navigation buttons -->
  <a href="<?php echo FIRST; ?>" role="button" class="btn btn-primary mt-2 mx-1<?php echo $disable_left ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_left ? 'true' : 'false'; ?>">&lt&lt</a>
  <a href="<?php echo $data['left_date']; ?>" role="button" class="btn btn-primary mt-2 mx-1<?php echo $disable_left ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_left ? 'true' : 'false'; ?>">&lt</a>
  <a href="random-comic" role="button" class="btn btn-primary mt-2 mx-1">Random</a>
  <a href="<?php echo $data['right_date']; ?>" role="button" class="btn btn-primary mt-2 mx-1<?php echo $disable_right ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_right ? 'true' : 'false'; ?>">&gt</a>
  <a href="<?php echo $data['latest_date']; ?>" role="button" class="btn btn-primary mt-2 mx-1<?php echo $disable_right ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_right ? 'true' : 'false'; ?>">&gt&gt</a>
  <br>

  <!-- Links to "dilbert.com" and the GitHub repo -->
  <a href="<?php echo $permalink; ?>" target="_blank" role="button" class="btn btn-link my-3 mx-1">Permalink</a>
  <div class="github mb-3">
    <a href="<?php echo GITHUB_REPO; ?>" target="_blank" class="btn btn-light">
      <span class="h5"><img src="static/resources/github.png" height="24" width="24"></span>
    </a>
  </div>

  </div>
</body>

</html>
