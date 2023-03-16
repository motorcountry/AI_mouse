from machine import Timer,PWM
import time

tim0 = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PWM)
tim1 = Timer(Timer.TIMER0, Timer.CHANNEL1, mode=Timer.MODE_PWM)
tim2 = Timer(Timer.TIMER0, Timer.CHANNEL2, mode=Timer.MODE_PWM)
c = PWM(tim0, freq=50, duty=0, pin=34) # enable=False
l = PWM(tim1, freq=50, duty=0, pin=17)
r = PWM(tim2, freq=50, duty=0, pin=13)

def Servo(servo,angle):
    servo.duty((angle+90)/180*10+2.5)


sensor_hmirror = False
sensor_vflip = 1
target_err_range = 10            # target error output range, default [0, 10]
target_ignore_limit = 0.02       # when target error < target_err_range*target_ignore_limit , set target error to 0
lcd_rotation = 2
lcd_mirror = True


import sensor,image,lcd
import KPU as kpu
class Target():
        def __init__(self, out_range=10, ignore_limit=0.02, hmirror=False, vflip=1, lcd_rotation=2, lcd_mirror=True):
            self.pitch = 0
            self.roll = 0
            self.out_range = out_range
            self.ignore = ignore_limit
            self.task_fd = kpu.load(0x300000) # face model addr in flash
            anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
            kpu.init_yolo2(self.task_fd, 0.5, 0.3, 5, anchor)
            lcd.init()
            lcd.rotation(lcd_rotation)
            lcd.mirror(lcd_mirror)
            sensor.reset()
            sensor.set_pixformat(sensor.RGB565)
            sensor.set_framesize(sensor.QVGA)
            if hmirror:
                sensor.set_hmirror(1)
            if vflip:
                sensor.set_vflip(1)

        def get_target_err(self):
            img = sensor.snapshot()
            code = kpu.run_yolo2(self.task_fd, img)
            if code:
                max_area = 0
                max_i = 0
                for i, j in enumerate(code):
                    a = j.w()*j.h()
                    if a > max_area:
                        max_i = i
                        max_area = a

                img = img.draw_rectangle(code[max_i].rect())
                self.pitch = (code[max_i].y() + code[max_i].h() / 2)/240*self.out_range*2 - self.out_range
                self.roll = (code[max_i].x() + code[max_i].w() / 2)/320*self.out_range*2 - self.out_range
                # limit
                if abs(self.pitch) < self.out_range*self.ignore:
                    self.pitch = 0
                if abs(self.roll) < self.out_range*self.ignore:
                    self.roll = 0
                img = img.draw_cross(160, 120)
                lcd.display(img)
                return (self.pitch, self.roll)
            else:
                img = img.draw_cross(160, 120)
                lcd.display(img)
                return (0, 0)

target = Target(target_err_range, target_ignore_limit, sensor_hmirror, sensor_vflip, lcd_rotation, lcd_mirror)


from Maix import GPIO, I2S
from fpioa_manager import fm

# user setting
sample_rate   = 16000
record_time   = 4  #s

c_mark = 0


Servo(c,-8)


fm.register(20,fm.fpioa.I2S0_IN_D0, force=True)
fm.register(18,fm.fpioa.I2S0_SCLK, force=True)
fm.register(19,fm.fpioa.I2S0_WS, force=True)

rx = I2S(I2S.DEVICE_0)
rx.channel_config(rx.CHANNEL_0, rx.RECEIVER, align_mode=I2S.STANDARD_MODE)
rx.set_sample_rate(sample_rate)
print(rx)

from speech_recognizer import isolated_word

# default: maix dock / maix duino set shift=0
sr = isolated_word(dmac=2, i2s=I2S.DEVICE_0, size=10, shift=0) # maix bit set shift=1
print(sr.size())
print(sr)

## threshold
sr.set_threshold(0, 0, 10000)

## record and get & set
while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(0):
    data = sr.get(0)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak dai_che')

while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(1):
    data = sr.get(1)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak kan_wo')

#sr.set(1, data)

while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(2):
    data = sr.get(2)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak lai')

while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(3):
    data = sr.get(3)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak zuo')

while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(4):
    data = sr.get(4)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak you')

while True:
  time.sleep_ms(100)
  print(sr.state())
  if sr.Done == sr.record(5):
    data = sr.get(5)
    print(data)
    break
  if sr.Speak == sr.state():
    print('speak tui')
#sr.set(3, data)

## recognizer
#sr.stop()
#sr.run()

print('recognizer')


while 1:
     # get target error

   c_angle = -40
   num = 11
   time.sleep_ms(200)
   if sr.Done == sr.recognize():
    res = sr.result()
    if isinstance(res, type(None)) or res[1] > 200:
      continue
    else:
      num = res[0]


    print(res)
  #  print(type(res))
  #  print(res[0])

   if num == 0:#带车
      if c_mark == 0:
         Servo(c,c_angle)
         c_mark = 1
         print('down')
      else:
         Servo(c,-10)
         c_mark = 0
         print('up')


   if num == 1:#跟随
    # print('heiio_hello')

     while 1:
        # err_roll = 0
         err_pitch, err_roll = target.get_target_err()
      #   time.sleep_ms(10)
      #   err_pitch, err_roll = target.get_target_err()
         print(err_roll,err_pitch)
         if err_roll > 1:
           print('rrrrrrrrrrrrrrrrrr')
           #l.enable()
           #r.enable()
           Servo(l,3)
           Servo(r,3)
           time.sleep_ms(50)
           #time.sleep(3)
           #l.disable()
           #r.disable()

         if err_roll <= 1 and err_roll >= -1 and err_roll != 0:
            print('break')
            Servo(l,0)
            Servo(r,0.5)
            sensor.shutdown(False)

            time.sleep_ms(50)
           # break

         if err_roll == 0:
            time.sleep_ms(50)
            continue


         if err_roll < -1:
            print('lllllllllllllllllll')
            #l.enable()
            #r.enable()
            Servo(l,-3)
            Servo(r,-3)
            time.sleep_ms(50)
            #l.disable()
            #r.disable()




         if err_pitch < -1 and c_angle >= -50:
            c_angle = c_angle - 5
            Servo(c,c_angle)
            print('uuuuuuuuuuuuuuuuuu')
            time.sleep_ms(50)

         if err_pitch == 0:
            time.sleep_ms(50)
            continue

         if err_pitch > 1 and c_angle <= -10:#脸在图片下半部分，收，偏向0度
            c_angle = c_angle + 5
            Servo(c,c_angle)
            print('dddddddddddddddddd')
            time.sleep_ms(50)

         if err_pitch >= -1 and err_pitch <= 1 and err_pitch != 0:
            Servo(c,c_angle)
            time.sleep_ms(50)


   if num == 2:#前进
     Servo(l,10)
     Servo(r,-10)
     time.sleep(3)
     Servo(l,0)
     Servo(r,0.5)
    #time.sleep(3)

   if num == 3:#左转
     Servo(l,-10)
     Servo(r,-10)
     time.sleep(1)
     Servo(l,0)
     Servo(r,0.5)

   if num == 4:#右转
     Servo(l,10)
     Servo(r,10)
     time.sleep(1)
     Servo(l,0)
     Servo(r,0.5)

   if num == 5:#退
     Servo(l,-10)
     Servo(r,10)
     time.sleep(1)
     Servo(l,0)
     Servo(r,0.5)
