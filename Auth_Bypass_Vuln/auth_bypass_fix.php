<?php

$config = array(
    'credentials' => array(
        'user' => 'admin',
        'password' =>
        '$argon2id$v=19$m=65536,t=4,p=1$TXqdqy9iNGRNhdkuRWZuYQsfTjXCFlKDPB8yfJGxLcpHybaaur7XeTCAbFyJkeERj4'
    ),
    'messages' => array(
        'access_denied' => 'Access denied!',
        'welcome' => "<p>Hello {$_SERVER['PHP_AUTH_USER']}!</p>",
        'recipe'  => "<p>Here is the secret recipe:"
    ),
    'secrets' => array(
        'french_crepe_recipe' => '1 cup flour, 2 eggs, ½ cup milk, ½ cup water, ½ teaspoon salt, 2 tablespoons butter'
    ),
    'color' => 'red'
);

extract($config);
if (isset($_REQUEST['color'])) {
    $color = $_REQUEST['color'];
}

function login($user, $pass) {
    if ($user !== $_SERVER['PHP_AUTH_USER'] || !password_verify($_SERVER['PHP_AUTH_PW'], $pass)) {
        header('WWW-Authenticate: Basic realm="AVCS 6"');
        header('HTTP/1.0 401 Unauthorized');
        exit($access_denied);
    }
}

if (!empty($credentials)) {
    login($credentials['user'], $credentials['password']);
}

$color = urlencode($color);
echo "<div style=\"background-color: {$color}; color: white;\">{$messages['welcome']}</div>";
echo $messages['recipe'] . " <b>{$secrets['french_crepe_recipe']}</b>";
