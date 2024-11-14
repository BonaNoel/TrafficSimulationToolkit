# TrafficSimulationToolkit

TrafficSimulationToolkit is a collection of two Python applications developed as part of a thesis on traffic modeling and visualization. The applications utilize the OpenStreetMap (OSM) data and traffic simulation technologies to analyze and visualize road networks and simulate traffic flows. Both applications are designed with a PyQt6 graphical user interface (GUI) and are compatible with Python 3.9. Note that the requirements.txt may contain unused packages.

## Applications

### 1. OSMGraphGenerator

OSMGraphGenerator leverages the **OSMnx** library to generate road networks from OpenStreetMap data. This application allows users to process and visualize traffic network graphs, specifically for locations like cities or other regions. The generated graphs can be used for further analysis or simulation.

#### Features:

- Downloads and processes OpenStreetMap (OSM) data.
- Creates traffic network graphs with OSMnx.
- Visualizes road networks.
- Supports customizable settings for data processing.
- Save networks as .graphml files

### 2. TrafficSim

TrafficSim uses the **UXSim** package to simulate traffic flows in a modeled road network. Users can run simulations based on the generated graphs from OSMGraphGenerator.

#### Features:

- Runs traffic simulations based on road network graphs.
- Provides a graphical interface for setting up and executing simulations.
- Displays real-time simulation results.
- Allows analysis of traffic patterns, congestion, and more.

### Contributing

If you would like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request.

### License

This project is provided as-is, and anyone is free to use, modify, and distribute it in any way they see fit. There is no warranty of any kind, express or implied. By using this project, you agree to do so at your own risk.
