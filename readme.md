# Data View Project

This project provides a web interface for viewing and managing data collected from a Modbus server. It uses FastAPI for the backend, SQLAlchemy for database interaction, and DataTables for the frontend.

## Features

*   **Data Acquisition:** Reads data from a Modbus server and stores it in a SQLite database.
*   **Web Interface:** Provides a web interface for viewing, filtering, and deleting data.
*   **DataTables Integration:** Uses DataTables for interactive table display with sorting and pagination.
*   **PDF Report Generation:** Generates PDF reports of the data.
*   **Batch Management:** Allows deleting data by batch ID or deleting all data.

## Prerequisites

*   Python 3.7+
*   pip
*   A Modbus server to connect to

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <project_directory>
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Configure Modbus connection:**

    Edit `config_parameters.py` to set the Modbus server IP address, port, register address, and other relevant parameters:

    ```python
    HOST_IP = "127.0.0.1"  # Replace with your Modbus server IP
    PORT = 502            # Replace with your Modbus server port
    REG_ADDR = 0          # Replace with your register address
    REG_NB = 11           # Replace with the number of registers to read
    SLEEP_TIME = 5        # Time in seconds between Modbus reads
    ```

2.  **Database:**

    The project uses a SQLite database (`register_data.db`) by default. The database file will be created automatically when the application runs. You can change the database URL in `main.py` if needed:

    ```python
    DATABASE_URL = "sqlite+aiosqlite:///./register_data.db"
    ```

## Running the Application

1.  **Start the application:**

    ```bash
    python main.py
    ```

    This will start the FastAPI server and the Modbus data acquisition process.

2.  **Access the web interface:**

    Open your web browser and go to `http://localhost:8000/view`.

## Usage

*   **View Data:** The main page displays the data in a DataTables table. You can sort, filter, and paginate the data using the DataTables controls.
*   **Filter by Batch ID:** Use the search box above the table to filter the data by Batch ID (register1).
*   **Generate Report:** Click the "Report Data" button to generate a PDF report of the currently filtered data.  You must filter by Batch ID first.
*   **Delete Batch:** Click the "Delete Batch" button to delete all data for the currently filtered Batch ID.  You must filter by Batch ID first.
*   **Delete All:** Click the "Delete All" button to delete all data in the database.

## API Endpoints

*   `/`: Redirects to `/view`.
*   `/data`: Returns all data as JSON.
*   `/view`: Renders the HTML page with the DataTables table.
*   `/report?filename=<filename>&batch_id=<batch_id>`: Generates a PDF report for the specified batch ID.
*   `/del_file/{filename}`: Deletes the specified PDF file.
*   `/del_batch?batch_id=<batch_id>`: Deletes all data for the specified batch ID.
*   `/del_all`: Deletes all data in the database.
*   `/filterData`: Returns data for DataTables with filtering, sorting, and pagination.

## Dependencies

*   FastAPI
*   uvicorn
*   SQLAlchemy
*   aiosqlite
*   Jinja2
*   python-multipart
*   pyModbusTCP
*   reportlab
*   pydantic

## Contributing

Contributions are welcome! Please submit a pull request with your changes.

## License

Open Source
