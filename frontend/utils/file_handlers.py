import os

class FileHandler:
    def handle_pdf(self, input_path, output_path):
        if not os.path.exists(input_path):
            print(f"Error: Input file {input_path} does not exist")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add your PDF reading logic here
        print(f"Reading PDF from {input_path}")
        print(f"Saving output to {output_path}")

    def handle_csv(self, input_path, output_path):
        if not os.path.exists(input_path):
            print(f"Error: Input file {input_path} does not exist")
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Add your CSV reading logic here
        print(f"Reading CSV from {input_path}")
        print(f"Saving output to {output_path}")