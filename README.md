# Simple USVs Simulator

This project provides a simple USV simulator for educational purpose. Users can test their control methods preliminarily in this simulator. The project is implemented using numpy and pyopengl so that everyone can easily run it with some lightweight libraries installed.

To get start
````
pip install numpy pyopengl scipy xlsxwriter pygame pywavefront pykalman serial xlrd==1.2.0
````

For single-boat cases, you can refer to demo1. For multiple-boat cases please refer to demo3. All you need to do is create a controller class which consists of a function called "update_state". The "update_state" function should take true wind and a USV's pose as input and output commands. 

The examples of configuration are under the folder "config". Feel free to play with parameters such as GUI_EN and save.
