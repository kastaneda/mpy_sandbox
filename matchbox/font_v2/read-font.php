#!/usr/bin/env php
<?php

$width = 1064;
$height = 392;
$padding = 20;

$px_size = 7;
$px_padding = 1;

$step = $px_size + $px_padding;

$filesToRead = [
    [
        'name' => '128x32.png',
        'glyphs' => [
            'ABCDEFGHIJKLMNPQRSTUVWXYZ',
            'abcdefghijklmnopqrstuvwxyz',
            'O0123456789',
            '!"#$%&\'()*+,-./:;<=>?@`[\\]^_{|}~',
        ],
    ],
    [
        'name' => 'cyrillic.png',
        'glyphs' => [
            'БГҐДЄЁЖЗИЇЙЛПУЎФЦЧШЩЪЫЬ',
            'ЭЮЯбвгґдєёжзиїйклмнптўфцч',
            'шщъыьэюя',
            '«»°–—©§•№⌘¶€£µÄäÖöÜüẞß▯',
        ],
    ],
];

$remap = require('same-glyph.php');

$font = [
    ' ' => '00000000',
];

foreach ($filesToRead as $fileToRead) {
    $im = imagecreatefrompng($fileToRead['name']);
    if (!$im) {
        echo 'Error opening file ' . $fileToRead['name'] . PHP_EOL;
        die();
    }

    if (imagesx($im) != $width || imagesy($im) != $height) {
        echo 'Error: image ' . $fileToRead['name'] . 
            ' must be ' . $width . 'x' . $height . PHP_EOL;
        die();
    }


    foreach ($fileToRead['glyphs'] as $lineNo => $glyphs) {
        $len = mb_strlen($glyphs);
        $baseX = $padding + ((int) ($step / 2));
        $baseY = $padding + ((int) ($step / 2)) + $lineNo * $step * 12;
        //echo "baseX=$baseX baseY=$baseY\n";
        $col = 0;
        for ($c = 0; $c < $len; $c++) {
            $char = mb_substr($glyphs, $c, 1);
            echo "\nReading char $char\n\n";
            $readBuf = '';
            do {
                $readByte = 0;
                $glyphEnds = false;
                for ($row = 0; $row < 8; $row++) {
                    $x = $baseX + $col * $step;
                    $y = $baseY + $row * $step;
                    //echo "col=$col row=$row x=$x y=$y\n";
                    $color = imagecolorat($im, $x, $y);
                    [
                        'red' => $r,
                        'green' => $g,
                        'blue' => $b,
                        'alpha' => $_,
                    ] = imagecolorsforindex($im, $color);
                    $rgb = ($r << 16) + ($g << 8) + $b;
                    //echo "r=$r g=$g b=$b ";
                    //echo  $rgb .PHP_EOL;
                    if ($rgb == 0) {
                        $glyphEnds = true;
                    } elseif ($rgb == 0x00ffff) {
                        $readByte += (1 << $row); // LSB top, MSB bottom
                    }
                }
                if (!$glyphEnds) {
                    $readBuf .= chr($readByte);
                    echo strtr(str_pad(decbin($readByte), 8, '0', STR_PAD_LEFT), '01', ' #') . PHP_EOL;
                }
                $col++;
            } while (!$glyphEnds);
            $font[$char] = bin2hex($readBuf);
        }
    }
}

$result = [
    'remap' => $remap,
    'glyph' => $font,
];

$json = json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
file_put_contents('font.json', $json);
