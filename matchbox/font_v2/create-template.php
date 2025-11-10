#!/usr/bin/env php
<?php

$width = 1064;
$height = 392;
$padding = 20;

$px_size = 7;
$px_padding = 1;

$lines = 4;

$im = imagecreate($width, $height);

$color_bg = imagecolorallocate($im, 0, 0, 0);       // black
$color_px = imagecolorallocate($im, 63, 63, 63);    // gray
$color_px1 = imagecolorallocate($im, 91, 91, 91);   // lighter gray
$color_fg = imagecolorallocate($im, 0, 255, 255);   // cyan

imagefilledrectangle($im, 0, 0, $width - 1, $height - 1, $color_bg);

$width_px = (int) (($width - $padding * 2) / ($px_size + $px_padding));

var_dump($width_px);

for ($line = 0; $line < $lines; $line++) {
    for ($pixel_x = 0; $pixel_x < $width_px; $pixel_x++) {
        for ($y = 0; $y < 8; $y++) {
            $start_x = $padding + ($px_size + $px_padding) * $pixel_x;
            $start_y = $padding + ($px_size + $px_padding) * $y
                + 12 * ($px_size + $px_padding) * $line;
            imagefilledrectangle($im,
                $start_x, $start_y,
                $start_x + $px_size - 1, $start_y + $px_size - 1,
                // WTF? I must add "- 1" or it doesn't work correct
                ($y < 2 || $y > 6) ? $color_px : $color_px1);
        }
    }
}

imagefilledrectangle($im,
    $padding, $padding,
    $padding + $px_size - 1, $padding + $px_size - 1,
    $color_fg);

imagepng($im, 'template.png');
