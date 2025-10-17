from machine import Pin, I2C
import ssd1306
#i2c = I2C(sda=Pin(8), scl=Pin(9))
i2c = I2C(0)
disp = ssd1306.SSD1306_I2C(128, 32, i2c)
disp.contrast(0)
disp.text('Hello, World!', 0, 0, 1)
disp.show()
