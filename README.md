# NeSPReSO Visualization Dashboard

A comprehensive web-based visualization dashboard for exploring NeSPReSO (Nested Spectral Resolution Ocean) data, providing interactive maps, profiles, and transects for oceanographic variables including temperature, salinity, sea surface height, and derived metrics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Conda or pip package manager
- NetCDF data files (NeSPReSO format)

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nespreso_viz
   ```

2. **Install dependencies**
   ```bash
   pip install dash dash-bootstrap-components xarray numpy plotly cmocean gsw
   ```

3. **Prepare your data**
   - Place your NeSPReSO NetCDF file in the `data/` directory
   - Update the file path in `nespreso_viz.py` (line 25)

4. **Run the application**
   ```bash
   python nespreso_viz.py
   ```

5. **Access the dashboard**
   - Open your browser and navigate to `http://localhost:8050`
   - The dashboard will load with interactive oceanographic visualizations

### Docker Quick Start (Alternative)
```bash
docker build -t nespreso-viz .
docker run -p 8050:8050 nespreso-viz
```

---

## 📖 Overview

NeSPReSO Viz is a sophisticated web application built with Dash that provides interactive visualization of oceanographic data from the NeSPReSO model. The dashboard enables researchers and oceanographers to explore complex 4D ocean data through an intuitive web interface.

### Key Features

- **Multi-panel visualization**: Satellite data, model predictions, profiles, and transects
- **Interactive data exploration**: Click to add profile locations, draw transect lines
- **Temporal navigation**: Date picker for time-series exploration
- **Depth-dependent analysis**: Slider for vertical depth selection
- **Real-time updates**: Dynamic figure updates based on user interactions
- **Professional styling**: Bootstrap-based responsive design

## 🏗️ Architecture

### Core Components

- **`nespreso_viz.py`**: Main application entry point with Dash callbacks
- **`viz_utils/`**: Modular utility classes for different visualization types
  - `styles.py`: UI layout and styling configuration
  - `update_main.py`: Main figure generation and updates
  - `update_prof.py`: Profile visualization management
  - `update_trans.py`: Transect visualization management
  - `ocean_utils.py`: Oceanographic calculations and utilities

### Data Structure

The application expects NetCDF files with the following variables:
- `Temperature`: 4D array (time, lat, lon, depth)
- `Salinity`: 4D array (time, lat, lon, depth)
- `SST`: Sea Surface Temperature (time, lat, lon)
- `SSS`: Sea Surface Salinity (time, lat, lon)
- `AVISO`: Sea Surface Height (time, lat, lon)
- `MLD`: Mixed Layer Depth (time, lat, lon)
- `OHC`: Ocean Heat Content (time, lat, lon)
- `Isotherm`: Isothermal depth (time, lat, lon)

## 🎯 Usage Guide

### Navigation

1. **Date Selection**: Use the calendar picker to select specific dates
2. **Depth Options**: Choose depth ranges for analysis (100m, 200m, 300m, 400m, or custom)
3. **Profile Locations**: Toggle 'Add Points' and click on any map to add profile points; use Undo/Clear in the profile controls when in use.
4. **Transect Lines**: Use the 'Draw line' tool to add a transect on any map; use Undo/Clear in the transect controls when in use.
5. **Clear Profiles**: Remove all profile locations with the clear button

### Visualization Panels

#### Satellite Data (Top Row)
- Toggle between a single map (default: AVISO) and all three using the 'Show all maps' switch.
- Select the single displayed field with the 'Field' dropdown.
- **AVISO**: Sea Surface Height anomalies [m]
- **SST**: Sea Surface Temperature from satellite [°C] (converted from Kelvin)
- **SSS**: Sea Surface Salinity from satellite [PSU]

#### NeSPReSO Predictions (Middle Row)
- Temperature and salinity maps now match satellite map sizes.
- Coastlines added and default bbox set to [lon: -99 to -81, lat: 18 to 30].
- **Temperature Maps**: Model-predicted temperature at selected depth [°C]
- **Salinity Maps**: Model-predicted salinity at selected depth [PSU]
- **Temperature Transects**: Cross-sectional temperature along drawn lines [°C]
- **Salinity Transects**: Cross-sectional salinity along drawn lines [PSU]
- **Temperature Profiles**: Vertical temperature profiles at selected locations [°C]
- **Salinity Profiles**: Vertical salinity profiles at selected locations [PSU]

#### Derived Metrics (Bottom Row)
- **MLD**: Mixed Layer Depth
- **OHC**: Ocean Heat Content
- **Isotherm**: Depth of specific isothermal surfaces

## 🔧 Configuration

### Customization Options

- **Color Schemes**: Modify colormaps in `styles.py`
- **Figure Heights**: Adjust panel dimensions in `NespresoStyles`
- **Data Sources**: Update file paths and data loading logic
- **UI Layout**: Modify the dashboard layout in `default_layout()`

### Environment Variables

```bash
export NESPRESO_DATA_PATH="/path/to/your/data"
export NESPRESO_HOST="0.0.0.0"
export NESPRESO_PORT="8050"
```

## 🚀 Deployment

### Production Deployment

1. **WSGI Configuration**
   ```bash
   # Update ozavala_custom_wsgi.conf with your server details
   # Configure Apache/Nginx to use the WSGI application
   ```

2. **Environment Setup**
   ```bash
   # Create production environment
   conda create -n nespreso-prod python=3.8
   conda activate nespreso-prod
   pip install -r requirements.txt
   ```

3. **Service Configuration**
   ```bash
   # Create systemd service file
   sudo systemctl enable nespreso-viz
   sudo systemctl start nespreso-viz
   ```

### Docker Deployment

```bash
# Build production image
docker build -f Dockerfile.prod -t nespreso-viz:prod .

# Run with environment variables
docker run -d \
  -p 8050:8050 \
  -e NESPRESO_DATA_PATH=/data \
  -v /path/to/data:/data \
  nespreso-viz:prod
```

## 🧪 Development

### Local Development

1. **Setup Development Environment**
   ```bash
   conda create -n nespreso-dev python=3.8
   conda activate nespreso-dev
   pip install -e .
   pip install -r requirements-dev.txt
   ```

2. **Run Tests**
   ```bash
   pytest tests/
   ```

3. **Code Quality**
   ```bash
   black nespreso_viz/
   flake8 nespreso_viz/
   mypy nespreso_viz/
   ```

### Project Structure

```
nespreso_viz/
├── nespreso_viz.py          # Main application
├── wsgi.py                  # WSGI entry point
├── viz_utils/               # Visualization utilities
│   ├── __init__.py
│   ├── styles.py            # UI styling and layout
│   ├── update_main.py       # Main figure updates
│   ├── update_prof.py       # Profile visualization
│   ├── update_trans.py      # Transect visualization
│   └── ocean_utils.py       # Oceanographic calculations
├── assets/                  # Static assets
│   ├── bootstrap.min.css
│   └── bootstrap-icons.min.css
├── data/                    # Data directory (not in repo)
├── requirements.txt          # Dependencies
└── README.md               # This file
```

## 📊 Data Requirements

### Input Data Format

- **File Format**: NetCDF4 (.nc)
- **Coordinate System**: Standard oceanographic (lat, lon, depth, time)
- **Time Resolution**: Daily or sub-daily
- **Spatial Resolution**: Configurable (typically 0.1° or finer)
- **Depth Levels**: Surface to 2000m (configurable)

### Data Quality

- **Missing Data**: Handled with NaN values
- **Data Validation**: Automatic range checking
- **Error Handling**: Graceful degradation for missing variables

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for all classes and methods
- Write tests for new functionality

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NeSPReSO Team**: For providing the oceanographic data and model
- **Dash Community**: For the excellent web framework
- **Oceanographic Community**: For feedback and testing

## 📞 Support

### Getting Help

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the inline code documentation
- **Community**: Join our discussion forum

### Contact Information

- **Maintainer**: [Your Name/Organization]
- **Email**: [contact@example.com]
- **Project URL**: [https://github.com/username/nespreso_viz]

---

**Note**: This dashboard is designed for oceanographic research and operational oceanography. Ensure you have proper data access permissions and follow data usage guidelines for your specific datasets.
