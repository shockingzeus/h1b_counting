
import sys
import csv
import re
from decimal import Decimal


states=['AK','AL','AR','AS','AZ','CA','CO','CT','DC','DE','FL','GA','GU','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD',
 'ME','MI','MN','MO','MP','MS','MT','NA','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK', 'OR','PA','PR','RI','SC',
 'SD','TN','TX','UT','VA','VI','VT','WA','WI','WV','WY']

class h1b_report:
    def __init__(self, file):
    # Initialize, load the data file. Find the relevant column from the headers (first line in file).
        self.f = open(file,newline = "") 
        self.reader = csv.reader(self.f, delimiter = ";",skipinitialspace = True )
        self.headers = next(self.reader)
        self.soc_index = self.find_index('SOC','CODE')
        self.name_index = self.find_index('SOC','NAME')
        self.status_index = self.find_index('STATUS')
        self.state_index = self.find_index('WORK','STATE')
    # Create dictionaries to keep track of the application numbers associated with each SOC_CODE or STATE
        self.soc_report = dict() 
        self.state_report = dict()
        self.name_report = dict()
        self.pattern = re.compile(r'^\d{2}-\d{4}')# The soc_code should follow "XX-XXXX" format.
        self.typo_state = [] # Dump for invalid data with possible typos in the "STATE" column.
        self.typo_soc = [] # Dump for invalid data with possible typos in the "SOC_CODE" column.
        
    def find_index(self,*args):
    # find the header through keywords 
        for i,header in enumerate(self.headers):
            if all(arg in header for arg in args):
                return i
        
    def process(self):
    # Process the data. Invalid data (probably due to typos) were filtered out and saved as lists for examination. 
    # Keep track of the number of the invalid data. If it is more than 0.1%, raise a warning.
        typo_count_state = 0
        typo_count_soc = 0
        total_count = 0
        for line in self.reader:
    # In case csv_reader fails
            if len(line)==1:
                line = line[0].rsplit(";")
    # Find the "certified" status
            if line[self.status_index].rstrip().lower()=='certified':
                total_count+=1
                soc = line[self.soc_index]
    # "Standardlize" the SOC_CODE. Invalid entries gives NONE object.
                soc = self.valid_soc(soc)
                name = line[self.name_index].rstrip()
                state = line[self.state_index]
    # Check if STATE make sense
                if state not in states:
                    self.typo_state.append(line)
                    typo_count_state+=1
    # Check if SOC_CODE is valid
                elif not soc:
                    self.typo_soc.append(line)
                    typo_count_soc+=1
    # Update the dictionaries with application numbers
                else:
                    self.update_report(soc, self.soc_report)
                    self.update_report(state, self.state_report)
                    self.update_name(soc, name)
                    
    # Check if too much data is invalid
        if total_count == 0:
            print("Warning - no certified record in this file.")
        else:
            if typo_count_state/total_count>0.001:
                print("Warning - {1} out of {2} records have errors in the STATE column.".format(typo_count_state,total_count))
            if typo_count_soc/total_count>0.001:
                print("Warning - {1} out of {2} records have errors in the SOC_CODE column.".format(typo_count_soc,total_count))
                   
    def update_report(self,tag, report_dict):
    # Update the dictionaries with application numbers
        if not tag:
            return
        elif tag not in report_dict:
            report_dict[tag]=1
        else:
            report_dict[tag]+=1  
            
    def update_name(self, soc, name):
    # Note that a single SOC_CODE may correspond to quite a few variations of SOC_NAME. 
    # Some of the SOC_NAME entry might even be empty - we refer it as "No Value".
    # So we keep track of the occurrence of SOC_NAME associated with SOC_CODE. 
    # We choose the SOC_NAME that occurs most frequently as the "default" SOC_NAME for that particular SOC_CODE. 
    # We do not consider the occurrence of "No Value" unless we have no other choice.
        name = name.strip("\"")
        if not name:
            name = "No Value"
        if soc not in self.name_report:
            self.name_report[soc] = {name:0} if name == "No Value" else {name:1}
        elif name not in self.name_report[soc]:
            new_item = {name:0} if name == "No Value" else {name:1}
            self.name_report[soc].update(new_item)
        else:
            addto = 0 if name == "No Value" else 1
            self.name_report[soc][name]+=addto
            
    def soc_to_name(self, soc):
    # get the SOC_NAME that occurs most frequently as the "default" SOC_NAME for that particular SOC_CODE.  
        names = self.name_report[soc]
        return max(names.keys(), key=(lambda key: names[key])) 

    
    def valid_soc(self, soc):
    # Check if the soc_code follows the right format. Convert soc_code to "\d\d-\d\d\d\d" if possible.
    # Invalid soc will return None. The associated data would be put in the dump for examination if necessary.
    # Some SOC_CODE has the format "\d\d-\d\d\d\d.\d\d" but we only need the code before the "." character.
        if self.pattern.match(soc):
            if len(soc.rstrip()) ==7:
                return soc
            elif soc[7] == ".":
                return soc[:7]
            else: 
                return None
        
    def top_state(self, output):
    # Sort the STATE dictionary. Output the top 10 to a file.
        total_num = sum(self.state_report.values())
        topstates = sorted(self.state_report.items(), key = lambda x:(-x[1], x[0]))
        with open(output,"w") as output:
            output.write(";".join(["TOP_STATES","NUMBER_CERTIFIED_APPLICATIONS","PERCENTAGE"])+"\n")
            for i in range(min(10,len(topstates))):
                state, num = topstates[i]
                ratio = Decimal(num/total_num)
                output.write(";".join([state, str(num), "{:.1%}".format(ratio)])+"\n")
                
    def top_soc(self, output):
    # Sort the SOC_CODE dictionary. Output the top 10 to a file.
        total_num = sum(self.soc_report.values())
        to_sort = [(self.soc_to_name(soc), value) for soc, value in self.soc_report.items()]
        top_soc = sorted(to_sort, key = lambda x:(-x[1], x[0]))
        with open(output,"w") as output:
            output.write(";".join(["TOP_OCCUPATIONS","NUMBER_CERTIFIED_APPLICATIONS","PERCENTAGE"])+"\n")
            for i in range(min(10,len(top_soc))):
                name, num = top_soc[i]
                ratio = Decimal(num/total_num)
                output.write(";".join([name, str(num), "{:.1%}".format(ratio)])+"\n")
                
    def close(self):
        if self.f:
            self.f.close()
            self.f = None   
            
def main(source, output1, output2):  
    import contextlib
    with contextlib.closing(h1b_report(source)) as report:
        report.process()
        report.top_soc(output1)
        report.top_state(output2)
    
if __name__=="__main__":
    main(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]))



