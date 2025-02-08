from fpdf import FPDF
from datetime import datetime
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

class PDF(FPDF):
    process_number = ""
    start_time = ""
    serial_number = ""
    end_time = ""
    time_interval = ""

    def setValues(self, process_number, start_time, serial_number, end_time, time_interval):
        self.process_number = process_number
        self.start_time = start_time
        self.serial_number = serial_number
        self.end_time = end_time
        self.time_interval = time_interval

    def header(self):
        self.set_font('Arial', 'B', 8)
        self.cell(0, 13, '', 0, 1, 'C')

    def add_table(self, data, filename, file_counter):
        self.set_font('Arial', 'B', 12)
        # Header
        self.cell(51, 10, ' Model', 1, 0, 'L')
        self.cell(74, 10, ' DISPAX REACTOR DR 2000/05', 1, 0, 'L')
        self.image('/modbus/static/logo.png', 160, self.get_y() + 1, w=100, h=28)
        self.cell(150, 30, '', 1, 0, 'C')
        fix_x = self.get_x()
        self.set_x(fix_x)
        self.cell(45, 10, ' Date', 1, 0, 'L')
        self.cell(80, 10, datetime.now().strftime("%d/%m/%Y"), 1, 1, 'C')  # Current date

        self.set_font('Arial', '', 12)
        # Second row
        self.cell(51, 10, ' Project Number', 1, 0, 'L')
        self.cell(74, 10, ' 20125620', 1, 0, 'L')
        self.set_x(fix_x)
        self.cell(45, 10, ' Set RPM', 1, 0, 'L')
        self.cell(80, 10, str(data[0][11]), 1, 1, 'C')  # Replace with actual data

        # Third row
        self.cell(51, 10, ' Serial Number / Batch ID', 1, 0, 'L')
        self.cell(74, 10, ' IB24-1367 / ' + str(int(data[0][2])), 1, 0, 'L')
        self.set_x(fix_x)
        self.cell(45, 10, ' Set Time', 1, 0, 'L')
        self.cell(80, 10, str(data[0][9]), 1, 1, 'C')  # Replace with actual data
        p_width = self.get_x()
        fix_y = self.get_y()
        self.cell(400, 10, "", 1, 1)  # Line break
        self.cell(51, 20, 'SL.NO', 1, 0, 'C')
        self.cell(74, 20, 'Date & Time', 1, 0, 'C')
        self.cell(35, 10, 'Motor Speed', 1, 0, 'C')
        self.cell(40, 10, 'Motor Current', 1, 0, 'C')
        self.cell(35, 10, 'Motor Torque', 1, 0, 'C')
        self.cell(40, 10, 'Motor Run Hour', 1, 0, 'C')
        self.cell(45, 10, 'Product Temperature', 1, 0, 'C')
        self.cell(40, 10, 'Tool Speed', 1, 0, 'C')
        self.cell(40, 10, 'Actual Time', 1, 1, 'C')
        self.set_xy(135, fix_y + 20)
        self.cell(35, 10, '(RPM)', 1, 0, 'C')
        self.cell(40, 10, '(Amps)', 1, 0, 'C')
        self.cell(35, 10, '(%)', 1, 0, 'C')
        self.cell(40, 10, '(Hour)', 1, 0, 'C')
        self.cell(45, 10, '(°C)', 1, 0, 'C')
        self.cell(40, 10, '(RPM)', 1, 0, 'C')
        self.cell(40, 10, '(Second)', 1, 1, 'C')
        # Table body
        self.set_font('Arial', '', 10)
        self.set_y(fix_y + 30)
        if len(data) > 0:

            for i in range(len(data)):
                date_str = data[i][1]  # "Thu Jan 25 23:06:12 2024"
                date_obj = datetime.strptime(date_str, "%a %b %d %H:%M:%S %Y")
                formatted_date = date_obj.strftime("%d/%m/%Y %H:%M:%S")

                self.cell(51, 10, str(i + 1), 1, 0, 'C')
                self.cell(74, 10, formatted_date, 1, 0, 'C')

                self.cell(35, 10, str(round(data[i][3], 2)), 1, 0, 'C')
                self.cell(40, 10, str(round(data[i][4], 2)), 1, 0, 'C')
                self.cell(35, 10, str(round(data[i][5], 2)), 1, 0, 'C')
                self.cell(40, 10, str(data[i][6]), 1, 0, 'C')
                self.cell(45, 10, str(round(data[i][7], 2)), 1, 0, 'C')
                self.cell(40, 10, str(round(data[i][8], 2)), 1, 0, 'C')
                self.cell(40, 10, str(data[i][10]), 1, 1, 'C')

        # Use in filename
        self.output(f'/modbus/{filename}')

@app.post("/print-db-to-pdf")
def print_db_to_pdf(batch_data: List[List], process_number: str = None, start_time: str = None, serial_number: str = None,
                    end_time: str = None, time_interval: str = None, file_counter: int = 0):
    print("printing....")

    pdf = PDF('L', 'mm', 'A3')  # 'L' for landscape mode, 'mm' for unit of measure, 'A3' for page size
    pdf.setValues(process_number, start_time, serial_number, end_time, time_interval)
    pdf.add_page()

    # Set the filename for the PDF file
    now = datetime.now()
    now_str = now.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'report_data_{now_str}.pdf'

    pdf.add_table(batch_data, filename, file_counter)
    # Set the MIME type for the PDF file
    mimetype = 'application/pdf'

    # Return the PDF file as a response
    return FileResponse(f'{filename}', media_type=mimetype, filename=filename)
