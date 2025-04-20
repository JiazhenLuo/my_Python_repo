import tkinter as tk
import random

root = tk.Tk()
root.title("Choose Your Phone Number")
root.geometry("600x200")

value = 0

def format_phone_number(val):
    s = str(int(val)).zfill(11)
    return f"({s[1:4]})-{s[4:7]}-{s[7:11]}"

phone_label = tk.Label(root, text = f"Please Enter Your Phone Number:\n{format_phone_number(value)}",font=("Arial",14))
phone_label.pack(pady=10)

slider = tk.Scale(root, from_=0, to=9999999999, orient="horizontal", length=300, resolution=1)
slider.set(value)
slider.pack()

def on_slider_change(val):
    phone_label.config(text=f"Please Enter Your Phone Number:\n{format_phone_number(val)}")

slider.config(command=on_slider_change)
root.mainloop()
