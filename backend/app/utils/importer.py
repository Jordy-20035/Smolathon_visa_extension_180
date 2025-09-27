import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import inspect
import uuid
from datetime import datetime
import io

logger = logging.getLogger(__name__)


class DataImporter:
    def __init__(self, db: Session):
        self.db = db

    def import_csv(self, file_content: bytes, model_class, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Import data from CSV file"""
        try:
            text = file_content.decode("utf-8", errors="replace")  # safer than BytesIO
            df = pd.read_csv(io.StringIO(text))
            return self._import_dataframe(df, model_class, column_mapping)
        except Exception as e:
            logger.error(f"CSV import error: {e}")
            raise ValueError(f"CSV import failed: {str(e)}")

    def import_excel(
        self, file_content: bytes, model_class, column_mapping: Dict[str, str], sheet_name: Optional[str] = 0
    ) -> Dict[str, Any]:
        """Import data from Excel file"""
        try:
            df = pd.read_excel(io.BytesIO(file_content), sheet_name=sheet_name)
            return self._import_dataframe(df, model_class, column_mapping)
        except Exception as e:
            logger.error(f"Excel import error: {e}")
            raise ValueError(f"Excel import failed: {str(e)}")

    def _import_dataframe(self, df: pd.DataFrame, model_class, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Process DataFrame and import data"""
        # Validate mapping
        self._validate_mapping(df.columns, column_mapping)

        # Rename columns
        df = df.rename(columns=column_mapping)

        # Normalize column names
        df.columns = [c.strip() for c in df.columns]

        # Convert DataFrame to records
        records = df.to_dict("records")

        return self._import_records(records, model_class)

    def _validate_mapping(self, file_columns: List[str], column_mapping: Dict[str, str]):
        """Ensure mapping keys exist in file"""
        for file_col in column_mapping.keys():
            if file_col not in file_columns:
                raise ValueError(f"Column '{file_col}' not found in uploaded file")

    def _import_records(self, records: List[Dict[str, Any]], model_class) -> Dict[str, Any]:
        successful = 0
        failed = 0
        errors = []

        for i, record in enumerate(records, 1):
            try:
                cleaned = self._clean_record(record, model_class)
                if not cleaned:
                    continue
                obj = model_class(**cleaned)
                self.db.add(obj)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(f"Row {i}: {str(e)}")
                logger.warning(f"Row {i} failed: {e}")

        if successful > 0:
            self.db.commit()

        return {
            "total_processed": len(records),
            "successful": successful,
            "failed": failed,
            "errors": errors,
        }

    def _clean_record(self, record: Dict[str, Any], model_class) -> Dict[str, Any]:
        cleaned = {}
        mapper = inspect(model_class)

        for key, value in record.items():
            if pd.isna(value) or value == "":
                continue

            if key not in mapper.columns:
                continue

            column = mapper.columns[key]
            cleaned[key] = self._convert_value(value, column.type)

        return cleaned

    def _convert_value(self, value, column_type):
        """Safe type conversion"""
        try:
            py_type = getattr(column_type, "python_type", str)

            if py_type == uuid.UUID:
                return uuid.UUID(str(value))

            if py_type == datetime:
                return pd.to_datetime(value, errors="coerce").to_pydatetime() if value else None

            if py_type in (int, float):
                return py_type(value)

            return py_type(value)

        except Exception as e:
            logger.warning(f"Conversion error for '{value}': {e}")
            return value


# ---- Model-specific importers ----

class FineImporter(DataImporter):
    def import_fines(
        self, file_content: bytes, file_type: str, column_mapping: Dict[str, str], sheet_name: Optional[str] = 0
    ) -> Dict[str, Any]:
        from app.models import Fine

        if file_type == "csv":
            return self.import_csv(file_content, Fine, column_mapping)
        elif file_type == "excel":
            return self.import_excel(file_content, Fine, column_mapping, sheet_name)
        else:
            raise ValueError("Unsupported file type")


class AccidentImporter(DataImporter):
    def import_accidents(
        self, file_content: bytes, file_type: str, column_mapping: Dict[str, str], sheet_name: Optional[str] = 0
    ) -> Dict[str, Any]:
        from app.models import Accident

        if file_type == "csv":
            return self.import_csv(file_content, Accident, column_mapping)
        elif file_type == "excel":
            return self.import_excel(file_content, Accident, column_mapping, sheet_name)
        else:
            raise ValueError("Unsupported file type")


class TrafficLightImporter(DataImporter):
    def import_traffic_lights(
        self, file_content: bytes, file_type: str, column_mapping: Dict[str, str], sheet_name: Optional[str] = 0
    ) -> Dict[str, Any]:
        from app.models import TrafficLight

        if file_type == "csv":
            return self.import_csv(file_content, TrafficLight, column_mapping)
        elif file_type == "excel":
            return self.import_excel(file_content, TrafficLight, column_mapping, sheet_name)
        else:
            raise ValueError("Unsupported file type")


class EvacuationImporter(DataImporter):
    def import_evacuations(
        self, file_content: bytes, file_type: str, column_mapping: Dict[str, str], sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        from app.models import Evacuation, Location
        
        try:
            if file_type == "excel":
                import openpyxl
                
                # First, ensure we have a location - let's check what's available
                print("Checking available locations...")
                
                # Get any existing location
                existing_location = self.db.query(Location).first()
                
                if existing_location:
                    print(f"Using existing location with ID: {existing_location.id}")
                    location_id = existing_location.id
                else:
                    # Create a new location if none exist
                    print("No locations found, creating a new one...")
                    
                    # Try to create with common location attributes
                    location_data = {'id': uuid.uuid4()}
                    
                    # Try to set name if the attribute exists
                    try:
                        if hasattr(Location, 'name'):
                            location_data['name'] = "Default Evacuation Location"
                        elif hasattr(Location, 'address'):
                            location_data['address'] = "City-wide evacuation data"
                        elif hasattr(Location, 'description'):
                            location_data['description'] = "Default evacuation location"
                    except:
                        pass  # If no text attributes, we'll just use the ID
                    
                    # Try to create the location
                    try:
                        new_location = Location(**location_data)
                        self.db.add(new_location)
                        self.db.commit()
                        location_id = new_location.id
                        print(f"Created new location with ID: {location_id}")
                    except Exception as e:
                        print(f"Error creating location: {e}")
                        # If we can't create a location, try to use a hardcoded UUID that might exist
                        location_id = uuid.uuid4()
                        print(f"Using generated location ID: {location_id}")
                
                wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
                
                print(f"Available sheets: {wb.sheetnames}")
                
                # Automatic sheet detection logic
                if sheet_name is None:
                    # Priority 1: Look for exact evacuation data sheets
                    target_sheets = []
                    for sheet in wb.sheetnames:
                        sheet_lower = sheet.lower()
                        if ('эвакуация' in sheet_lower or 'evacuation' in sheet_lower) and 'маршрут' not in sheet_lower:
                            target_sheets.append(sheet)
                    
                    if target_sheets:
                        # Prefer sheets with year numbers (more likely to be data sheets)
                        year_sheets = [s for s in target_sheets if any(str(year) in s for year in range(2020, 2030))]
                        if year_sheets:
                            sheet_name = year_sheets[0]
                        else:
                            sheet_name = target_sheets[0]
                        print(f"Auto-selected evacuation data sheet: {sheet_name}")
                    else:
                        # Priority 2: Look for any sheet that's not a route/map sheet
                        non_route_sheets = []
                        for sheet in wb.sheetnames:
                            sheet_lower = sheet.lower()
                            if not any(term in sheet_lower for term in ['маршрут', 'route', 'map', 'аналитик', 'пример']):
                                non_route_sheets.append(sheet)
                        
                        if non_route_sheets:
                            sheet_name = non_route_sheets[0]
                            print(f"Auto-selected non-route sheet: {sheet_name}")
                        else:
                            # Priority 3: Use the first sheet as last resort
                            sheet_name = wb.sheetnames[0]
                            print(f"Using first sheet as fallback: {sheet_name}")
                else:
                    print(f"Using provided sheet: {sheet_name}")
                
                sheet = wb[sheet_name]
                
                print(f"Selected sheet: {sheet.title}")
                print(f"Dimensions: {sheet.max_row} rows x {sheet.max_column} columns")
                
                # Smart data detection - find where the actual data starts
                header_row = None
                first_data_row = None
                
                # Look for the header row (contains column names like "Дата", "Количество эвакуаторов", etc.)
                header_keywords = ['дата', 'эвакуатор', 'выезд', 'эвакуация', 'поступление', 'date', 'vehicle', 'dispatch', 'revenue']
                
                for row_num in range(1, min(20, sheet.max_row + 1)):  # Check first 20 rows
                    # Check multiple cells in the row for header keywords
                    header_match_count = 0
                    for col in range(1, min(6, sheet.max_column + 1)):  # Check first 5 columns
                        cell_value = sheet.cell(row=row_num, column=col).value
                        if cell_value and isinstance(cell_value, str):
                            cell_lower = cell_value.lower()
                            if any(keyword in cell_lower for keyword in header_keywords):
                                header_match_count += 1
                    
                    if header_match_count >= 2:  # If at least 2 cells match header keywords
                        header_row = row_num
                        first_data_row = row_num + 1  # Data starts after header
                        print(f"Found header at row {header_row}")
                        break
                
                # If no header found, try to find the first row with date data
                if first_data_row is None:
                    for row_num in range(1, min(20, sheet.max_row + 1)):
                        date_cell = sheet.cell(row=row_num, column=1).value
                        if date_cell and (isinstance(date_cell, datetime) or 
                                         (isinstance(date_cell, str) and 
                                          any(year in str(date_cell) for year in ['2024', '2025', '2023']))):
                            first_data_row = row_num
                            print(f"Found data starting at row {first_data_row} (date detected)")
                            break
                
                # Final fallback
                if first_data_row is None:
                    first_data_row = 4  # Default assumption
                    print(f"Using default data start row: {first_data_row}")
                
                # Print the detected header and first few data rows for verification
                print(f"\nHeader row {header_row}:" if header_row else "No header row detected")
                if header_row:
                    header_data = []
                    for col in range(1, min(6, sheet.max_column + 1)):
                        header_data.append(sheet.cell(row=header_row, column=col).value)
                    print(f"Header: {header_data}")
                
                print(f"\nFirst 5 data rows (starting from row {first_data_row}):")
                for i in range(first_data_row, min(first_data_row + 5, sheet.max_row + 1)):
                    row_data = []
                    for col in range(1, min(6, sheet.max_column + 1)):
                        row_data.append(sheet.cell(row=i, column=col).value)
                    print(f"Row {i}: {row_data}")
                
                # Now process the actual data
                success_count = 0
                error_count = 0
                errors = []
                
                for row_num in range(first_data_row, sheet.max_row + 1):
                    try:
                        # Get cell values
                        date_cell = sheet.cell(row=row_num, column=1).value
                        vehicles_cell = sheet.cell(row=row_num, column=2).value
                        dispatches_cell = sheet.cell(row=row_num, column=3).value
                        evacuations_cell = sheet.cell(row=row_num, column=4).value
                        revenue_cell = sheet.cell(row=row_num, column=5).value
                        
                        # Skip empty rows
                        if date_cell is None:
                            continue
                            
                        # Skip if it's actually a header row (contains text but no date)
                        if isinstance(date_cell, str) and not any(year in date_cell for year in ['2024', '2025', '2023']):
                            if any(keyword in date_cell.lower() for keyword in header_keywords):
                                continue
                        
                        print(f"Processing row {row_num}: Date={date_cell}")
                        
                        # Parse date
                        evacuated_at = None
                        if date_cell:
                            if isinstance(date_cell, datetime):
                                evacuated_at = date_cell
                            elif isinstance(date_cell, str):
                                try:
                                    # Clean the date string
                                    date_str = date_cell.strip()
                                    if ' ' in date_str:
                                        evacuated_at = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                    else:
                                        evacuated_at = datetime.strptime(date_str, '%Y-%m-%d')
                                except ValueError:
                                    # Try other date formats if needed
                                    continue
                        
                        if not evacuated_at:
                            continue
                        
                        # Create evacuation record with the location ID
                        evacuation_data = {
                            'evacuated_at': evacuated_at,
                            'towing_vehicles_count': int(vehicles_cell) if vehicles_cell is not None else 0,
                            'dispatches_count': int(dispatches_cell) if dispatches_cell is not None else 0,
                            'evacuations_count': int(evacuations_cell) if evacuations_cell is not None else 0,
                            'revenue': float(revenue_cell) if revenue_cell is not None else 0.0,
                            'location_id': location_id,  # Use the location ID we found/created
                            'visibility': 'private'
                        }
                        
                        evacuation = Evacuation(**evacuation_data)
                        self.db.add(evacuation)
                        success_count += 1
                        
                        if success_count % 50 == 0:
                            self.db.commit()
                            print(f"Committed {success_count} records...")
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Row {row_num}: {str(e)}")
                        print(f"Error on row {row_num}: {e}")
                        continue
                
                self.db.commit()
                print(f"Import completed: {success_count} successful, {error_count} failed")
                
                return {
                    "total_processed": sheet.max_row - first_data_row + 1,
                    "successful": success_count,
                    "failed": error_count,
                    "errors": errors
                }
                
        except Exception as e:
            self.db.rollback()
            import traceback
            print(f"Import error: {str(e)}")
            print(traceback.format_exc())
            raise Exception(f"Excel import failed: {str(e)}")