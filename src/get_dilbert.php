<?php

function get_dilbert_data($comic)
{
  static $cache;  # Static for making it persist in memory, if required
  if (file_exists(CACHE_FILE))
  {
    $cache_json = file_get_contents(CACHE_FILE);
    $cache = json_decode($cache_json, true);  # "true" supplied to decode into an associative array
  }
  else
    $cache = array();

  $now = new DateTime("now");
  $data = array();
  $data['last'] = $now->format(FORMAT);  # Time stored for checking "freshness" of cached data

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
  if (
    array_key_exists($cache_key, $cache) &&
    ($now->diff(new DateTime($cache[$cache_key]['last']))->format('s') < CACHE_REFRESH)
  )
    return $cache[$comic];

  # Get the latest comic for getting its date
  $curl_handle = curl_init();
  curl_setopt($curl_handle, CURLOPT_URL, "http://dilbert.com/strip/" . $now->format(FORMAT));
  curl_setopt($curl_handle, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($curl_handle, CURLOPT_FOLLOWLOCATION, true);
  curl_exec($curl_handle);
  $resp_url = curl_getinfo($curl_handle, CURLINFO_EFFECTIVE_URL);
  curl_close($curl_handle);
  $data['latest'] = end(explode("/", $resp_url));  # Split by "/" and get the last element

  if ($comic === "latest")
  {
    # Get actual latest comic
    $comic_date = new DateTime($data['latest']);
    $comic = $data['latest'];
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
  $data['url'] = $matches[1];

  # Get the date (eg. "April 28, 2019")
  preg_match('/<date class="comic-title-date" item[pP]rop="datePublished">[^<]*<span>([^<]*)<\/span>[^<]*<span item[pP]rop="copyrightYear">([^<]+)<\/span>/', $content, $matches);
  $date = $matches[1] . " " . $matches[2];
  $data['date'] = $date;

  # Get the title, if it exists; else empty string
  preg_match('/<span class="comic-title-name">([^<]+)<\/span/', $content, $matches);
  $data['name'] = (count($matches) > 0) ? $matches[1] : '';

  # Parse the actual comic date; this is done as if the date is wrong, dilbert.com redirects to the closest comic date
  $comic_date = DateTime::createFromFormat('D M d, Y', $date);
  $comic = $comic_date->format(FORMAT);
  $data['current'] = $comic;

  # The dates of the comics before and after the current one
  $comic_date->sub(new DateInterval('P1D'));
  $data['left'] = max(new DateTime(FIRST), $comic_date)->format(FORMAT);
  $comic_date->add(new DateInterval('P2D'));  # adding 2 days to compensate for earlier subtraction
  $data['right'] = min(new DateTime($data['latest']), $comic_date)->format(FORMAT);

  # This is done to ensure that this cache item is the latest in the cache array (as arrays in PHP are sorted by insertion order)
  # This orders the cache by the "freshness"
  if (array_key_exists($comic, $cache))
    unset($cache[$comic]);
  $cache[$comic] = $data;
  # Delete the 1st item if the limit is reached
  if (count($cache) > CACHE_LIMIT)
    array_shift($cache);

  # Save cache to disk (disk used as caching in memory requires special server)
  file_put_contents(CACHE_FILE, json_encode($cache), FILE_USE_INCLUDE_PATH);

  return $data;
}

?>
