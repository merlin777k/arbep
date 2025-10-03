#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Raspberry Pi Servo Control Dashboard
Compatible with Python 2.7 and Python 3.x
"""

import serial
import time
import os
import sys
import termios
import tty
import glob

class ServoController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connected = False
        self.running = False
        self.speed = 15
        self.reverse_mode = False
        self.servo1_pos = 90
        self.servo2_pos = 90
        
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            self.connected = True
            print("Connected to Arduino on " + str(port))
        except Exception as e:
            print("Could not connect to " + str(port))
            print("Error: " + str(e))
            print("Running in simulation mode")
    
    def clear_screen(self):
        os.system('clear')
    
    def send_command(self, command):
        if self.connected:
            try:
                self.ser.write((command + "\n").encode())
            except Exception as e:
                print("Error sending command: " + str(e))
    
    def get_key(self):
        """Get single keypress without waiting for Enter"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            # Handle arrow keys (they send 3 characters)
            if ch == '\x1b':
                ch = ch + sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def display_dashboard(self):
        self.clear_screen()
        print("=" * 60)
        print("       RASPBERRY PI SERVO CONTROL")
        print("=" * 60)
        print("")
        
        if self.running:
            print("Status: RUNNING")
        else:
            print("Status: STOPPED")
        
        if self.connected:
            print("Connection: Connected")
        else:
            print("Connection: Disconnected")
        
        print("Speed Delay: " + str(self.speed) + "ms")
        
        if self.reverse_mode:
            print("Reverse Mode: ON")
        else:
            print("Reverse Mode: OFF")
        
        print("Servo 1 Position: " + str(self.servo1_pos) + " degrees")
        print("Servo 2 Position: " + str(self.servo2_pos) + " degrees")
        
        print("")
        print("-" * 60)
        print("CONTROLS:")
        print("-" * 60)
        print("  [SPACE]    Start/Stop Auto Sweep")
        print("  [UP]       Move Servo 1 Forward (+5 degrees)")
        print("  [DOWN]     Move Servo 1 Backward (-5 degrees)")
        print("  [LEFT]     Move Servo 2 Backward (-5 degrees)")
        print("  [RIGHT]    Move Servo 2 Forward (+5 degrees)")
        print("  [1]        Set Fast Speed (15ms)")
        print("  [2]        Set Medium Speed (100ms)")
        print("  [3]        Set Slow Speed (333ms)")
        print("  [R]        Toggle Reverse Mode")
        print("  [M]        Menu Mode")
        print("  [Q]        Quit")
        print("-" * 60)
        print("")
        print("Press any key for control...")
    
    def display_menu(self):
        self.clear_screen()
        print("=" * 50)
        print("    MENU MODE")
        print("=" * 50)
        print("")
        print("  1. Start Sweep")
        print("  2. Stop Sweep")
        print("  3. Set Fast Speed (15ms)")
        print("  4. Set Medium Speed (100ms)")
        print("  5. Set Slow Speed (333ms)")
        print("  6. Toggle Reverse Mode")
        print("  7. Change Port")
        print("  8. Back to Control Mode")
        print("-" * 50)
        print("")
    
    def change_port(self):
        self.clear_screen()
        print("Current port: " + str(self.port))
        print("")
        
        try:
            new_port = raw_input("Enter new port (e.g., /dev/ttyUSB0): ").strip()
        except NameError:
            new_port = input("Enter new port (e.g., /dev/ttyUSB0): ").strip()
        
        if new_port:
            try:
                if self.connected:
                    self.ser.close()
                
                self.ser = serial.Serial(new_port, self.baudrate, timeout=1)
                time.sleep(2)
                self.connected = True
                self.port = new_port
                print("Connected to " + str(new_port))
            except Exception as e:
                self.connected = False
                print("Could not connect to " + str(new_port))
                print("Error: " + str(e))
            
            time.sleep(2)
    
    def menu_mode(self):
        while True:
            self.display_menu()
            
            try:
                choice = raw_input("Enter choice (1-8): ").strip()
            except NameError:
                choice = input("Enter choice (1-8): ").strip()
            
            if choice == '1':
                self.running = True
                self.send_command("START")
                print("Sweep started!")
                time.sleep(1)
            elif choice == '2':
                self.running = False
                self.send_command("STOP")
                print("Sweep stopped!")
                time.sleep(1)
            elif choice == '3':
                self.speed = 15
                self.send_command("SPEED:15")
                print("Speed set to 15ms")
                time.sleep(1)
            elif choice == '4':
                self.speed = 100
                self.send_command("SPEED:100")
                print("Speed set to 100ms")
                time.sleep(1)
            elif choice == '5':
                self.speed = 333
                self.send_command("SPEED:333")
                print("Speed set to 333ms")
                time.sleep(1)
            elif choice == '6':
                self.reverse_mode = not self.reverse_mode
                if self.reverse_mode:
                    self.send_command("REVERSE:1")
                    print("Reverse mode ON")
                else:
                    self.send_command("REVERSE:0")
                    print("Reverse mode OFF")
                time.sleep(1)
            elif choice == '7':
                self.change_port()
            elif choice == '8':
                break
            else:
                print("Invalid choice! Please enter 1-8")
                time.sleep(1)
    
    def run(self):
        while True:
            self.display_dashboard()
            
            key = self.get_key()
            
            if key == 'q' or key == 'Q':
                print("")
                print("Shutting down...")
                if self.connected:
                    self.send_command("STOP")
                    self.ser.close()
                break
            
            elif key == ' ':
                self.running = not self.running
                if self.running:
                    self.send_command("START")
                else:
                    self.send_command("STOP")
            
            elif key == '\x1b[A':  # Up arrow
                self.servo1_pos = min(180, self.servo1_pos + 5)
                self.send_command("SERVO1:" + str(self.servo1_pos))
            
            elif key == '\x1b[B':  # Down arrow
                self.servo1_pos = max(0, self.servo1_pos - 5)
                self.send_command("SERVO1:" + str(self.servo1_pos))
            
            elif key == '\x1b[C':  # Right arrow
                self.servo2_pos = min(180, self.servo2_pos + 5)
                self.send_command("SERVO2:" + str(self.servo2_pos))
            
            elif key == '\x1b[D':  # Left arrow
                self.servo2_pos = max(0, self.servo2_pos - 5)
                self.send_command("SERVO2:" + str(self.servo2_pos))
            
            elif key == '1':
                self.speed = 15
                self.send_command("SPEED:15")
            
            elif key == '2':
                self.speed = 100
                self.send_command("SPEED:100")
            
            elif key == '3':
                self.speed = 333
                self.send_command("SPEED:333")
            
            elif key == 'r' or key == 'R':
                self.reverse_mode = not self.reverse_mode
                if self.reverse_mode:
                    self.send_command("REVERSE:1")
                else:
                    self.send_command("REVERSE:0")
            
            elif key == 'm' or key == 'M':
                self.menu_mode()
            
            time.sleep(0.1)

def find_arduino_ports():
    """Find all possible Arduino serial ports"""
    ports = []
    
    # Common Arduino port patterns on Linux/Raspberry Pi
    patterns = [
        '/dev/ttyUSB*',
        '/dev/ttyACM*',
        '/dev/ttyAMA*',
        '/dev/serial/by-id/*Arduino*',
        '/dev/cu.usbserial*',
        '/dev/cu.usbmodem*'
    ]
    
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    return sorted(set(ports))

def test_arduino_connection(port, baudrate=9600):
    """Test if port is an Arduino by trying to connect"""
    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        time.sleep(2)
        ser.close()
        return True
    except Exception as e:
        return False

def main():
    print("=" * 50)
    print("  Raspberry Pi Servo Controller")
    print("=" * 50)
    print("")
    print("Searching for Arduino...")
    print("")
    
    # Find all possible Arduino ports
    available_ports = find_arduino_ports()
    
    if not available_ports:
        print("No serial devices found!")
        print("")
        try:
            port = raw_input("Enter port manually: ").strip()
        except NameError:
            port = input("Enter port manually: ").strip()
        
        if not port:
            port = '/dev/ttyUSB0'
    else:
        print("Found serial devices:")
        for i, p in enumerate(available_ports):
            status = "OK" if test_arduino_connection(p) else "?"
            print("  " + str(i+1) + ". " + p + " [" + status + "]")
        
        print("")
        
        try:
            choice = raw_input("Select port (1-" + str(len(available_ports)) + ") or Enter for auto: ").strip()
        except NameError:
            choice = input("Select port (1-" + str(len(available_ports)) + ") or Enter for auto: ").strip()
        
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_ports):
                port = available_ports[idx]
            else:
                port = available_ports[0]
        else:
            # Auto-select first working port
            port = available_ports[0]
            for p in available_ports:
                if test_arduino_connection(p):
                    port = p
                    break
        
        print("")
        print("Using port: " + port)
        time.sleep(1)
    
    controller = ServoController(port=port, baudrate=9600)
    controller.run()

if __name__ == "__main__":
    main()