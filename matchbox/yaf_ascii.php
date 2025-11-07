#!/usr/bin/env php
<?php

$im = imagecreatefrompng('yaf_ascii.png');

/*
$char = 'G';
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
*/

function readGlyph(int $char): array
{
    global $im;
    $char_x = ($char - 32) & 0x0F;
    $char_y = ($char - 32) >> 4;
    $glyph = [];
    for ($x = 0; $x < 8; $x++) {
        $col = 0;
        for ($y = 0; $y < 8; $y++) {
            $rgb = imagecolorat(
                $im,
                $char_x*36 + $x*4 + 1,
                $char_y*36 + $y*4 + 1
            );
            $px = match ($rgb) {
                0x3000FF => 1,
                0xFFFF00 => 0,
                default => null,
            };
            if ($px === null) {
                return $glyph;
            }
            $col += $px << $y;
        }
        $glyph[] = $col;
    }
    return $glyph;
}

/*
$glyph = readGlyph(ord('G'));
foreach ($glyph as $col) {
    echo str_pad(decbin($col), 8, '0', STR_PAD_LEFT) . PHP_EOL;
}
*/

$font = [];
for ($char = 32; $char <= 126; $char++) {
    $gl = readGlyph($char);
    array_shift($gl);
    array_pop($gl);
    $font[$char] = array_values($gl);
}

file_put_contents('ascii.php', '<?php return ' . var_export($font, true) . ';');
