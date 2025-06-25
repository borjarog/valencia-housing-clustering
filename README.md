# Valencia Housing Clustering Analysis

## Overview

This project provides a comprehensive analysis of the real estate market in Valencia, Spain, using data mining and clustering techniques. The application includes an interactive dashboard built with Dash that visualizes housing data, market trends, and geographical distributions of properties.

## Features

### 📊 Interactive Dashboard
- **Real-time filtering**: Filter properties by constructed area, price range, and number of rooms
- **Geographical visualization**: Interactive maps showing property distributions across Valencia
- **Market analysis**: Price correlations, neighborhood comparisons, and quality metrics
- **Clustering results**: Geographical distribution of properties grouped by characteristics

### 🗺️ Data Visualizations
- **Scatter maps**: Property locations with color-coded attributes
- **Choropleth maps**: Neighborhood-level statistics (quality, age)
- **Bar charts**: Property counts by neighborhood and room numbers
- **Box plots**: Price distributions across neighborhoods
- **Correlation analysis**: Price relationships with other variables

### 🔍 Clustering Analysis
- **K-means clustering**: Groups properties based on multiple characteristics
- **Geographical clustering**: Visual representation of property clusters
- **Feature analysis**: Price, area, rooms, bathrooms, age, and location-based clustering

## Project Structure

```
valencia-housing-clustering/
├── app/
│   ├── app.py                 # Main Dash application
│   └── assets/
│       └── style.css.css      # Custom styling
├── data/
│   ├── valencia_sale.csv              # Original housing data
│   ├── valencia_sale_clustered.csv    # Data with cluster assignments
│   ├── valencia_polygons.csv          # Neighborhood boundaries
│   └── valencia_metro.csv             # Metro station locations
├── raw-data/
│   ├── valencia_metro.xlsx
│   ├── valencia_polygons.xlsx
│   └── valencia_sale.xlsx
├── scripts/
│   ├── clustering.ipynb       # Clustering analysis notebook
│   ├── data_mining.ipynb      # Data exploration notebook
│   └── data_processing.py     # Data preprocessing scripts
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd valencia-housing-clustering
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Dashboard

1. **Navigate to the app directory**
   ```bash
   cd app
   ```

2. **Run the Dash application**
   ```bash
   python app.py
   ```

3. **Access the dashboard**
   - Open your web browser
   - Go to `http://localhost:8080`
   - The dashboard will load with all visualizations

### Dashboard Features

#### Interactive Filters
- **Constructed Area Slider**: Filter properties by square meters
- **Price Range Slider**: Set minimum and maximum price ranges
- **Room Number Dropdown**: Select specific number of bedrooms

#### Data Sections
1. **Summary Statistics**: Total properties, top neighborhoods, new construction
2. **Interactive Map**: Filtered property locations with price coloring
3. **Market Analysis**: Construction types, neighborhood distributions
4. **Quality & Age Maps**: Choropleth maps by neighborhood
5. **Price Analysis**: Correlation charts and box plots
6. **Clustering Results**: Geographical distribution of property clusters

## Data Sources

The project uses several datasets:

- **valencia_sale.csv**: Main housing dataset with property characteristics
- **valencia_polygons.csv**: Geographic boundaries for Valencia neighborhoods
- **valencia_metro.csv**: Metro station locations and information
- **valencia_sale_clustered.csv**: Processed data with cluster assignments

## Clustering Methodology

The clustering analysis uses K-means algorithm with the following features:
- **Price**: Property sale price
- **Constructed Area**: Square meters of the property
- **Room Number**: Number of bedrooms
- **Bath Number**: Number of bathrooms
- **Age**: Property age
- **Distance to City Center**: Proximity to Valencia's center
- **Distance to Metro**: Distance to nearest metro station
- **Distance to Blasco**: Distance to Blasco Ibáñez area
- **Cadastral Quality**: Property quality index

## Technologies Used

- **Dash**: Interactive web application framework
- **Plotly**: Interactive plotting and visualization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **GeoPandas**: Geographic data processing
- **Shapely**: Geometric operations
- **Scikit-learn**: Machine learning (clustering)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Data sources: Valencia real estate market data
- Universidad Politécnica de Valencia

## Contact

For questions or support, please open an issue in the repository.