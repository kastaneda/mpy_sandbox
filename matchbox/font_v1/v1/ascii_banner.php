#!/usr/bin/env php
<?php

//$msg = 'Hello, world!';
//$msg = 'strlen($msg);';
$msg = $argv[1] ?? 'Quick brown fox';
//$msg = 'jumps over the';
//$msg = 'Pixel craft';
$font = require 'ascii.php';

$banner = [];

for ($i = 0; $i < strlen($msg); $i++) {
    $nextGlyph = $font[ord($msg[$i])];
    if (count($banner)) {
        $lastCol = $banner[array_key_last($banner)];
        $nextCol = $nextGlyph[0];
        $intersect = ($lastCol & $nextCol)
            || ($lastCol & ($nextCol<<1))
            || (($lastCol<<1) & $nextCol);
        if ($intersect) {
            $banner = array_merge($banner, [0], $nextGlyph);
        } else {
            $banner = array_merge($banner, $nextGlyph);
        }
    } else {
        $banner = $nextGlyph;
    }
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
