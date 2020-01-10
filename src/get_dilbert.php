<?php

function init_cache($conn)
{
  # Create cache table if not exists
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
    die(pg_last_error());

  # Create index if not exists for efficient lookup
  $index_query = "CREATE INDEX IF NOT EXISTS idx_last_used ON cache (last_used);";
  $status = pg_query($conn, $index_query);
  if (!$status)
    die(pg_last_error());
}

function cache_data($conn, $data, $comic)
{
  # Check if it already exists; if yes, update, else insert
  $comic_query = "SELECT * FROM cache WHERE comic = $1;";
  $result = pg_query_params($conn, $comic_query, array($comic));
  if (!$result)
    die(pg_last_error());
  elseif (pg_num_rows($result) > 0)
  {
    # Assuming that only last_used and latest_date are changed
    $update_query = "
      UPDATE cache
      SET last_used = DEFAULT, latest_date = $1
      WHERE comic = $2;
    ";
    $result = pg_query_params($conn, $update_query, array($data['latest_date'], $comic));
  }
  else
  {
    $insertion_order = array(
      'latest_date', 'img_url', 'date_str', 'actual_date', 'title', 'left_date', 'right_date', 'comic'
    );
    $insert_query = "
      INSERT INTO cache (" . implode(', ', $insertion_order) . ")
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8);
    ";
    $data['comic'] = $comic;
    $params = array();
    foreach ($insertion_order as $key)
      array_push($params, $data[$key]);  # Appends to $params
    $result = pg_query_params($conn, $insert_query, $params);
  }
  if (!$result)
    die(pg_last_error());

  # Get number of items in cache
  $length_query = "SELECT COUNT(*) FROM cache;";
  $result = pg_query($conn, $length_query);
  if (!$result)
    die(pg_last_error());
  # Delete the old items from cache if length exceeds limit
  $num_rows = pg_fetch_result($result, 0, 'count');
  if($num_rows > CACHE_LIMIT)  # Exceeding limit of cache
  {
    $delete_query = "
      DELETE FROM cache
      WHERE ctid in (
        SELECT ctid FROM cache ORDER BY last_used LIMIT 1
      )
    ";
    $result = pg_query($conn, $delete_query);
    if (!$result)
      die(pg_last_error());
  }
}

function get_curl_info($url)
{
  $now = new DateTime("now");

  # Setup the handle for getting the comic webpage's contents
  $comic_handle = curl_init();
  curl_setopt($comic_handle, CURLOPT_URL, $url);
  curl_setopt($comic_handle, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($comic_handle, CURLOPT_FOLLOWLOCATION, true);

  # Setup the handle for getting the latest date
  $latest_date_handle = curl_init();
  curl_setopt($latest_date_handle, CURLOPT_URL, SOURCE_PREFIX . $now->format(FORMAT));
  curl_setopt($latest_date_handle, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($latest_date_handle, CURLOPT_FOLLOWLOCATION, true);

  # Handle to do async cURL for both handles at the same time
  $multi_handle = curl_multi_init();
  curl_multi_add_handle($multi_handle, $comic_handle);
  curl_multi_add_handle($multi_handle, $latest_date_handle);

  # Execute them both
  do
  {
    $curl_status = curl_multi_exec($multi_handle, $curl_active);
  } while ($curl_active && ($curl_status == CURLM_OK));

  # Close the multi-handle; only single handles needed
  curl_multi_remove_handle($multi_handle, $comic_handle);
  curl_multi_remove_handle($multi_handle, $latest_date_handle);
  curl_multi_close($multi_handle);

  # Get the comic webpage's contents
  $content = curl_multi_getcontent($comic_handle);
  # Get the latest comic's URL
  # This relies on "dilbert.com" auto-redirecting to the latest comic
  $resp_url = curl_getinfo($latest_date_handle, CURLINFO_EFFECTIVE_URL);
  $latest_date = end(explode("/", $resp_url));  # Split by "/" and get the last element

  # Close the single handles too
  curl_close($comic_handle);
  curl_close($latest_date_handle);

  return array($content, $latest_date);
}

function get_dilbert_data($conn, $comic)
{
  # Initialize cache if not exists
  init_cache($conn);
  $now = new DateTime("now");
  $data = array();

  # Check and see if date format is correct
  try
  {
    if ((!preg_match('/^\d{4}-\d{2}-\d{2}$/', $comic)) && ($comic !== 'now'))
      throw new Exception('Invalid date format provided');
    $comic_date = new DateTime($comic);
    $comic_date = min(max($comic_date, new DateTime(FIRST)), $now);
  }
  catch (Exception $exception)
  {
    # Invalid date format provided; so go to latest comic
    $comic_date = $now;
    $comic = $comic_date->format(FORMAT);
  }

  # If comic in cache and not old
  $comic_query = "SELECT * FROM cache WHERE comic = $1 AND last_used >= CURRENT_TIMESTAMP - INTERVAL '" . CACHE_REFRESH . " hours';";
  $result = pg_query_params($conn, $comic_query, array($comic_date->format(FORMAT)));
  if (!$result)
    die(pg_last_error());
  elseif (pg_num_rows($result) > 0)  # Found in cache
    return pg_fetch_array($result, 0, PGSQL_ASSOC);  # Return the row as an associative array

  # Get the comic webpage's contents and the latest comic (for getting its date)
  # Multiple returns (as an array) are stored into LHS using list
  list($content, $data['latest_date']) = get_curl_info(SOURCE_PREFIX . $comic_date->format(FORMAT));

  # Get the URL of the comic image
  preg_match('/<img[^>]*class="img-[^>]*src="([^"]+)"[^>]*>/', $content, $matches);
  $data['img_url'] = $matches[1];

  # Get the date (eg. "April 28, 2019")
  preg_match(
    '/<date class="comic-title-date" item[pP]rop="datePublished">[^<]*<span>([^<]*)<\/span>[^<]*<span item[pP]rop="copyrightYear">([^<]+)<\/span>/',
    $content,
    $matches
  );
  $date = $matches[1] . " " . $matches[2];
  $data['date_str'] = $date;

  # Parse the actual comic date; this is done as if the date is wrong, dilbert.com redirects to the closest comic date
  $comic_date = DateTime::createFromFormat('D M d, Y', $date);
  $data['actual_date'] = $comic_date->format(FORMAT);

  # Get the title, if it exists; else empty string
  preg_match('/<span class="comic-title-name">([^<]+)<\/span/', $content, $matches);
  $data['title'] = (count($matches) > 0) ? $matches[1] : '';

  # The dates of the comics before and after the current one
  $comic_date->sub(new DateInterval('P1D'));
  $data['left_date'] = max(new DateTime(FIRST), $comic_date)->format(FORMAT);
  $comic_date->add(new DateInterval('P2D'));  # adding 2 days to compensate for earlier subtraction
  $data['right_date'] = min(new DateTime($data['latest_date']), $comic_date)->format(FORMAT);

  # Store in cache
  cache_data($conn, $data, $data['actual_date']);

  return $data;
}

?>
