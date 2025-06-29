from typing import List, Optional
import csv

class Convertor:
    @staticmethod
    def extract_text(initial_file:str) -> Optional[List[str]]:
            try:
                with open(initial_file,'r') as txt_file:
                      txt_data = txt_file.readlines() # this would return list of the lines in the file
                      return txt_data
            except FileNotFoundError:
                print(f"Error: The file '{initial_file}' was not found.")
                return None
            except IOError:
                print(f"Error: Unable to read the file '{initial_file}'.")
                return None
    @staticmethod
    def pars_line(lines: List[str]) -> List[List[str]]:
            word_list = []  # Initialize an empty list to store words from each line
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                words = line.split()  # Split the line into words
                word_list.append(words)  # Add the list of words to the main list
            return word_list

    @staticmethod
    def extract_wp(words: List[List[str]]) -> List[List[str]]:
        wp =[]
        for word in words:
            if word[0] == "QGC" or word[1] == "1":
                continue
            lat,lon,alt= word[8],word[9],word[10]
            wp.append([lat,lon,alt])
        return wp

    def convert_to_csv(self,initial_file:str,target_file:str):
        text_data = self.extract_text(initial_file)
        word_list = self.pars_line(text_data)
        wp_list= self.extract_wp(word_list)
        with open(target_file, mode='w', newline='') as file:
            writer = csv.writer(file, delimiter=' ')
            writer.writerow(['lat','long','alt'])
            writer.writerows(wp_list)