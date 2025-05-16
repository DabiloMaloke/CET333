import json
import csv
import pandas as pd
from datetime import datetime
import os

def export_data(file_format='csv', time_range='last_hour'):
    """
    Export dashboard data in various formats
    
    Parameters:
    - file_format: 'csv', 'excel', or 'json'
    - time_range: 'last_hour', 'today', or 'all'
    """
    try:
        # Load the latest data
        with open("dashboard_data.json", "r") as f:
            current_data = json.load(f)
        
        # Create export directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"exports/dashboard_export_{timestamp}"
        
        # Prepare data for export
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_requests': current_data['total_requests'],
            'unique_visitors': current_data['unique_visitors'],
            'status_codes': current_data['status_counts'],
            'endpoints': current_data['top_endpoints']
        }
        
        # Convert to DataFrame for CSV/Excel exports
        status_df = pd.DataFrame({
            'status_code': list(export_data['status_codes'].keys()),
            'count': list(export_data['status_codes'].values())
        })
        
        endpoints_df = pd.DataFrame({
            'endpoint': list(export_data['endpoints'].keys()),
            'requests': list(export_data['endpoints'].values())
        })
        
        # Export based on selected format
        if file_format == 'csv':
            filename += '.csv'
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Timestamp', export_data['timestamp']])
                writer.writerow(['Total Requests', export_data['total_requests']])
                writer.writerow(['Unique Visitors', export_data['unique_visitors']])
                writer.writerow([])
                writer.writerow(['Status Code', 'Count'])
                for code, count in export_data['status_codes'].items():
                    writer.writerow([code, count])
                writer.writerow([])
                writer.writerow(['Endpoint', 'Requests'])
                for endpoint, requests in export_data['endpoints'].items():
                    writer.writerow([endpoint, requests])
            
        elif file_format == 'excel':
            filename += '.xlsx'
            with pd.ExcelWriter(filename) as writer:
                pd.DataFrame([{
                    'Timestamp': export_data['timestamp'],
                    'Total Requests': export_data['total_requests'],
                    'Unique Visitors': export_data['unique_visitors']
                }]).to_excel(writer, sheet_name='Summary', index=False)
                
                status_df.to_excel(writer, sheet_name='Status Codes', index=False)
                endpoints_df.to_excel(writer, sheet_name='Endpoints', index=False)
                
        elif file_format == 'json':
            filename += '.json'
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=4)
        
        return True, filename
    
    except Exception as e:
        return False, str(e)

def generate_report():
    """Generate a formatted PDF report (placeholder for future implementation)"""
    # This would require additional libraries like ReportLab or WeasyPrint
    pass

if __name__ == "__main__":
    # Example usage
    success, result = export_data(file_format='excel')
    if success:
        print(f"Export successful: {result}")
    else:
        print(f"Export failed: {result}") 
