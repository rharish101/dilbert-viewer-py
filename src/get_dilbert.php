<?php

function get_dilbert_data($conn, $comic)
{
  # Initialize cache if not exists
  $cache_init_query = "
    CREATE TABLE IF NOT EXISTS cache (
      comic DATE NOT NULL,
      last_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
      actual_date DATE NOT NULL,
      date_str VARCHAR(255) NOT NULL,
      img_url VARCHAR(255) NOT NULL,
      title VARCHAR(255) NOT NULL,
      left_date DATE NOT NULL,
      right_date DATE NOT NULL,
      latest_date DATE NOT NULL,
      PRIMARY KEY (comic)
    );
  ";
  $status = pg_query($conn, $cache_init_query);
  if (!$status)
    die("Error: " . pg_last_error());

  # Create index if not exists for efficient lookup
  $index_query = "CREATE INDEX IF NOT EXISTS idx_last_used ON cache (last_used);";
  $status = pg_query($conn, $index_query);
  if (!$status)
    die("Error: " . pg_last_error());

  $now = new DateTime("now");
  $data = array();

  if ($comic === "latest")
  {
    # Initialization done now for checking inside arr
    $comic_date = $now;
    $cache_key = $comic_date->format(FORMAT);
  }
  else
  {
    try
    {
      $comic_date = new DateTime($comic);
      $comic_date = min(max($comic_date, new DateTime(FIRST)), $now);
      $cache_key = $comic;
    }
    catch (Exception $exception)
    {
      # Invalid date format provided
      die("Error: " . $exception->getMessage());
    }
  }

  # If comic in cache and not old
  $comic_query = "SELECT * FROM cache WHERE comic = $1 AND last_used >= CURRENT_TIMESTAMP - INTERVAL '" . CACHE_REFRESH . " hours';";
  $result = pg_query_params($conn, $comic_query, array($cache_key));
  if (!$result)
    die('Error: ' . pg_last_error());
  elseif (pg_num_rows($result) > 0)
    return pg_fetch_array($result, 0, PGSQL_ASSOC);  # Return the row as an associative array

  # Get the latest comic for getting its date
  $curl_handle = curl_init();
  curl_setopt($curl_handle, CURLOPT_URL, "http://dilbert.com/strip/" . $now->format(FORMAT));
  curl_setopt($curl_handle, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl_handle, CURLOPT_FOLLOWLOCATION, true);
  curl_exec($curl_handle);
  $resp_url = curl_getinfo($curl_handle, CURLINFO_EFFECTIVE_URL);
  curl_close($curl_handle);
  $data['latest_date'] = end(explode("/", $resp_url));  # Split by "/" and get the last element

  if ($comic === "latest")
  {
    # Get actual latest comic
    $comic_date = new DateTime($data['latest_date']);
    $comic = $data['latest_date'];
  }

  # Get the comic webpage's contents
  $curl_handle = curl_init();
  curl_setopt($curl_handle, CURLOPT_URL, "http://dilbert.com/strip/" . $comic);
  curl_setopt($curl_handle, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl_handle, CURLOPT_FOLLOWLOCATION, true);
  $content = curl_exec($curl_handle);
  curl_close($curl_handle);

  # Get the URL of the comic image
  preg_match('/<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>/', $content, $matches);
  $data['img_url'] = $matches[1];

  # Get the date (eg. "April 28, 2019")
  preg_match('/<date class="comic-title-date" item[pP]rop="datePublished">[^<]*<span>([^<]*)<\/span>[^<]*<span item[pP]rop="copyrightYear">([^<]+)<\/span>/', $content, $matches);
  $date = $matches[1] . " " . $matches[2];
  $data['date_str'] = $date;

  # Parse the actual comic date; this is done as if the date is wrong, dilbert.com redirects to the closest comic date
  $comic_date = DateTime::createFromFormat('D M d, Y', $date);
  $comic = $comic_date->format(FORMAT);
  $data['actual_date'] = $comic;

  # Get the title, if it exists; else empty string
  preg_match('/<span class="comic-title-name">([^<]+)<\/span/', $content, $matches);
  $data['title'] = (count($matches) > 0) ? $matches[1] : '';

  # The dates of the comics before and after the current one
  $comic_date->sub(new DateInterval('P1D'));
  $data['left_date'] = max(new DateTime(FIRST), $comic_date)->format(FORMAT);
  $comic_date->add(new DateInterval('P2D'));  # adding 2 days to compensate for earlier subtraction
  $data['right_date'] = min(new DateTime($data['latest_date']), $comic_date)->format(FORMAT);

  # Check if it already exists; if yes, update, else insert
  $comic_query = "SELECT * FROM cache WHERE comic = $1;";
  $result = pg_query_params($conn, $comic_query, array($comic));
  if (!$result)
    die('Error: ' . pg_last_error());
  elseif (pg_num_rows($result) > 0)
  {
    $update_query = "
      UPDATE cache
      SET last_used = DEFAULT, img_url = $1, latest_date = $2
      WHERE comic = $3;
    ";
    $result = pg_query_params($conn, $update_query, array($data['img_url'], $data['latest_date'], $comic));
  }
  else
  {
    $insert_query = "
      INSERT INTO cache (latest_date, img_url, date_str, actual_date, title, left_date, right_date, comic)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
    ";
    $data['comic'] = $comic;
    $result = pg_query_params($conn, $insert_query, $data);
  }
  if (!$result)
    die('Error: ' . pg_last_error());

  # Delete the old items from cache
  $length_query = "SELECT comic FROM cache;";
  $result = pg_query($conn, $length_query);
  if (!$result)
    die('Error: ' . pg_last_error());
  elseif(pg_num_rows($result) > CACHE_LIMIT)
  {
    $delete_query = "
      DELETE FROM cache
      WHERE ctid in (
        SELECT ctid FROM cache ORDER BY last_used LIMIT 1
      )
    ";
  }

  return $data;
}

?>
