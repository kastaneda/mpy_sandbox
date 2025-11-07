#!/usr/bin/env php
<?php

$im = imagecreatefrompng('yaf_ascii.png');

$char = 'G';

$char_x = (ord($char) - 32) & 0x0F;
$char_y = (ord($char) - 32) >> 4;

echo 'Char ' . $char . PHP_EOL;
echo 'Column=' . $char_x . ', row=' . $char_y . PHP_EOL;

for ($y = 0; $y < 8; $y++) {
    for ($x = 0; $x < 8; $x++) {
        $rgb = imagecolorat(
            $im,
            $char_x*36 + $x*4 + 1,
            $char_y*36 + $y*4 + 1
        );
        //$r = ($rgb >> 16) & 0xFF;
        //$g = ($rgb >> 8) & 0xFF;
        //$b = $rgb & 0xFF;
        echo match ($rgb) {
            0x3000FF => '##',
            0xFFFF00 => '--',
            default => '..',
        };
        echo ' ';
    }
    echo PHP_EOL;
}
