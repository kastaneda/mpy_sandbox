#!/usr/bin/env php
<?php

//$msg = 'Hello, world!';
//$msg = 'strlen($msg);';
$msg = 'Quick brown fox';
$font = require 'ascii.php';

$banner = [];

$prev = '';
for ($i = 0; $i < strlen($msg); $i++) {
    $next = $msg[$i];
    $nextGlyph = $font[ord($msg[$i])];
    if (count($banner)) {
        if ($prev == 'f' && $next == 'o') {
            $banner = array_merge($banner, $nextGlyph);
        } else {
            $banner = array_merge($banner, [0], $nextGlyph);
        }
    } else {
        $banner = $nextGlyph;
    }
    $prev = $next;
}

for($y = 0; $y < 8; $y++) {
    foreach ($banner as $col) {
        if ($col & (1 << $y)) {
            echo '##';
        } else {
            echo '  ';
        }
    }
    echo PHP_EOL;
}
