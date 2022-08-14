__version__ = '0.3'
def extract_fil_format_from_layout(layout_file_name):
    """
    Function intended to extract the FIL file layotout from a .layout format for later use to read the .FIL file.
    
    input: STRING with the layout file name
    output: a list with field name, field type, field start and field end used for interpreting the .FIL file 
    """
    import codecs
    import re
    line_size = -1
    fields = []
    with codecs.open(layout_file_name, encoding='utf-16') as f:
        for line in f:
            if line_size != -1:
                line_list = re.split("\s+",line)
                #print(line_list)
                if len(line_list) == 5:
                    fields.append({'field_name':line_list[0],
                                   'field_type':line_list[1],
                                   'field_start':int(line_list[2])-1,
                                   'field_end':int(line_list[2])+int(line_list[3])-1})
                else:
                    break
            if 'RECORD_LENGTH' in line:
                line_size = (repr(line)).split(' ')[1]
                #print("line_size={}".format(line_size))
    return fields, int(line_size)



def convert_fil_to_csv_using_layout(data_file_name, layout_file_name):
    """
    Function to convert FIL file layotout using a layout format and a .FIL file into CSV format.
    
    input: data_file_name STRING, layout_file_name STRING
    output: the name of the CSV file generated
    """    
    fil_file_layout, line_size = extract_fil_format_from_layout(layout_file_name)
    csv_file_name = data_file_name.replace(".FIL",".csv") 
    file1 = open(csv_file_name,"w")

    file1.write(','.join([item['field_name'] for item in fil_file_layout]))

    with open(data_file_name,"r+") as f:
        for line in f:
            for i in range(int(len(line)/line_size)):
    #            print(i)
                temp_el = []
                for item in fil_file_layout: 
                    start = i*line_size+item['field_start']
                    end = i*line_size+item['field_end']
                    temp_el.append(line[start:end])
                file1.write(','.join(temp_el)+"\n")

    file1.close()
    return csv_file_name
