<!DOCTYPE HTML>
<html lang="en">

<head>
  <title><?php echo $title; ?>Dilbert Viewer</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
  <link rel="stylesheet" href="static/styles.css">
  <link rel="icon" type="image/png" href="static/favicon.png" sizes="96x96">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body class="text-center">
  <!-- Date and title (if exists) -->
  <div class="h4 mx-1 my-2"><?php echo $data['date_str']; ?></div>
  <div class="h6 m-1"><?php echo $data['title']; ?></div>

  <!-- Comic image -->
  <img class="img-fluid my-3 px-2" alt="<?php echo $data['actual_date']; ?>" src="<?php echo $data['img_url']; ?>"></img>

  <!-- Navigation buttons -->
  <div class="m-2">
    <a href="<?php echo FIRST; ?>" role="button" class="btn btn-primary m-1<?php echo $disable_left ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_left ? 'true' : 'false'; ?>">&lt&lt</a>
    <a href="<?php echo $data['left_date']; ?>" role="button" class="btn btn-primary m-1<?php echo $disable_left ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_left ? 'true' : 'false'; ?>">&lt</a>
    <a href="random-comic" role="button" class="btn btn-primary m-1">Random</a>
    <a href="<?php echo $data['right_date']; ?>" role="button" class="btn btn-primary m-1<?php echo $disable_right ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_right ? 'true' : 'false'; ?>">&gt</a>
    <a href="<?php echo $data['latest_date']; ?>" role="button" class="btn btn-primary m-1<?php echo $disable_right ? ' disabled' : ''; ?>" aria-disabled="<?php echo $disable_right ? 'true' : 'false'; ?>">&gt&gt</a>
  </div>

  <!-- Links to "dilbert.com" and the GitHub repo -->
  <a href="<?php echo $permalink; ?>" target="_blank" role="button" class="btn btn-link m-1">Permalink</a>
  <a href="<?php echo GITHUB_REPO; ?>" target="_blank" class="btn btn-light m-1">
    <img src="static/github.png" height="24" width="24">
  </a>
</body>

</html>
