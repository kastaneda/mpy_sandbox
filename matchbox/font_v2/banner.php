#!/usr/bin/env php
<?php

$msg = $argv[1] ?? 'Hello, world!';

$font = json_decode(file_get_contents('font.json'), true);

$out = '';
$len = mb_strlen($msg);

for ($c = 0; $c < $len; $c++) {
    $char = mb_substr($msg, $c, 1);
    $char = $font['remap'][$char] ?? $char;
    $glyph = $font['glyph'][$char] ?? $font['glyph']['▯'];
    $glyph = hex2bin($glyph);

    if ($out == '') {
        $out = $glyph;
    } else {
        // single-pixel "kerning", lol
        $prev = ord($out[-1]);
        $next = ord($glyph[0]);
        if (($prev & $next) || ($prev>>1 & $next) || ($prev & $next>>1)) {
            // we need add 1px indent between glyphs
            $out .= chr(0) . $glyph;
        } else {
            // pixels in those glyphs are not touching
            $out .= $glyph;
        }
    }
}

$len = strlen($out);
for ($y = 0; $y < 8; $y++) {
    for ($x = 0; $x < $len; $x++) {
        if ((1<<$y) & ord($out[$x])) {
            echo '##';
        } else {
            echo '  ';
        }
    }
    echo PHP_EOL;
}
