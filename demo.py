import Simulator
import YourController
import YourObserver

your_controller=YourController.controller()
your_observer=YourObserver.observer()
your_simulator=Simulator.simulator(total_step=1000,simulation_cycle=0.01,controller=your_controller,
                                    observer=your_observer,GUI=True)
your_simulator.run()

