"""
Paul Marshall and Phoebe Argon
Database Project 2
CS 457 -- UNR
3/27/18
"""

import os
import re
from contextlib import contextmanager #needed for multiple file opening

globalScopeDirectory = ""
workingDirectory = ""


def main():

    locking_array = ["table"]
    lock_flag = 0
    lock_index = 1

    try:
        if not os.path.exists("./locks"):  # create locking mech if not there
            os.makedirs("./locks")
        while True:
            command = ""
            #print locking_array, lock_flag
            if lock_flag is 1:
                if lock_index is not len(locking_array):
                    command = locking_array[lock_index]
                    lock_index += 1
                else:
                    toRemove = "./locks/" + locking_array[0]
                    if os.path.isfile(toRemove):
                        os.remove(toRemove)
                    locking_array = ["table"]
                    lock_index = 1
                    lock_flag = 0

            if lock_flag is not 1:
                while not ";" in command and not "--" in command:
                    command += raw_input("\n enter a command \n").strip('\r')  #Read command command from terminal
                command = command.split(";")[0]  #Remove ; from the command command



            command_string = str(command)  #Normalize the command command
            command_string = command_string.upper()

            if "--" in command:  # Pass the comments to find command
                pass

            elif "ALTER TABLE" in command_string:
                alter_table(command)

            elif "CREATE DATABASE" in command_string:
                create_db(command)

            elif "CREATE TABLE" in command_string:
                create_table(command)

            elif "DELETE FROM" in command_string:
                delete_from(command)

            elif "DROP DATABASE" in command_string:
                drop_db(command)

            elif "DROP TABLE" in command_string:
                drop_table(command)

            elif "INSERT INTO" in command_string:
                insert_into(command)

            elif "SELECT" in command_string:
                select_in(command, command_string)

            elif "UPDATE" in command_string:
                update_from(command)

            elif "USE" in command_string:
                use_db(command)

            elif "BEGIN TRANSACTION" in command_string:
                locking_array, lock_flag = transaction(locking_array, lock_flag)

            elif ".EXIT" in command:  # Exit database if specified
                print "All done."
                exit()

    except (EOFError, KeyboardInterrupt) as e:  # Exit script
        print "\n All done."


# Helper Functions
@contextmanager
def multi_file_manager(files, mode='rt'):
    """ Open multiple files and make sure they all get closed. """
    files = [open(file, mode) for file in files]
    yield files
    for file in files:
        file.close()

def use_enabled():  # Catch the error when a database hasn't been enabled
    if globalScopeDirectory is "":
        raise ValueError("!Failed to use table because no database was selected")
    else:
        global workingDirectory
        workingDirectory = os.path.join(os.getcwd(), globalScopeDirectory)


def get_column(data):
    column_index = data[0].split(" | ")
    for x in range(len(column_index)):
        column_index[x] = column_index[x].split(" ")[0]

    return column_index


def separate(line):
    line_tester = line.split(" | ")
    for x in range(len(line_tester)):  # Check that each column has an item
        line_tester[x] = line_tester[x].split(" ")[0]
    return line_tester


def join_where(search_item, table_varibles, data_array, join_type = 'inner'):
    
    counter = 0
    out = []
    flag = 0
    num_tables = len(data_array)
    matched_data = []
    empty_cols = ""

    #collect column data in array
    #check if column data matches

    if "=" in search_item:  # Evaluate operator
        if "!=" in search_item:
            r_col = search_item.split(" !=")[0]
        else:
            left_search = search_item.split(" =")[0]
            left_search = left_search.split(".")[1]

        right_search = search_item.split("= ")[1]
        right_search = right_search.split(".")[1]


    if num_tables == 2:
        left_table = data_array[0]
        right_table = data_array[1]
    else:
        print "!JOIN ONLY ACCEPTS TWO TABLES"
        return -1, -1

    left_data = []
    right_data = []

    left_column = get_column(left_table[0])
    right_column = get_column(right_table[0])
    
    for line in left_table:
    #if not left_search in line:
        #print line
        line_seperated = separate(line)
        left_data.append(line_seperated[left_column.index(left_search)])
            

    for line in right_table:
        line_seperated = separate(line)
        right_data.append(line_seperated[right_column.index(right_search)])

    #both inner and out joins start with matching data
    for x in range(len(left_data)):
        for y in range(len(right_data)):
            if left_data[x] == right_data[y]:
                right_table[y] = right_table[y].strip('\n')
                out.append(right_table[y] + ' | ' + left_table[x])
                counter += 1

                if join_type == 'left':
                    matched_data.append(left_table[x])

    if join_type == 'left':
        number_of_data = len(right_column)

        for x in range(number_of_data):
            empty_cols += ' | '

        for x in range(len(left_data)):
            if not left_column[0] in left_table[x]: #remove the table key

                if not left_table[x] in matched_data: #dont run unless no matches with this data
                    out.append(left_table[x].strip('\n') + empty_cols )
                    counter += 1

    return counter, out

    #attempt = [for data[num_tables]]


def where(search_arg, action, data, up_val=""):

    counter = 0
    column_index = get_column(data)
    attr_name = column_index
    input_data = list(data)
    out = []
    flag = 0

    if "=" in search_arg:  # Evaluate operator
        if "!=" in search_arg:
            r_col = search_arg.split(" !=")[0]
            flag = 1
        else:
            r_col = search_arg.split(" =")[0]

        search_arg = search_arg.split("= ")[1]

        if "\"" in search_arg or "\'" in search_arg: #gets rid of \n or \r
            search_arg = search_arg[1:-1]

        for line in data:
            line_test = separate(line)

            if search_arg in line_test: #if matched
                column_index = attr_name.index(r_col) 
                line_index = line_test.index(search_arg)
                if line_index == column_index:  #double check if matched field is correct field

                    if action == "delete":
                        del input_data[input_data.index(line)]  # Remove matching field
                        out = input_data
                        counter += 1
                    if action == "select":
                        out.append(input_data[input_data.index(line)])
                    if action == "update":
                        attribute, field = up_val.split(" = ")
                        if attribute in attr_name:
                            sep_line = separate(line)
                            sep_line[attr_name.index(attribute)] = field.strip().strip("'")
                            input_data[input_data.index(line)] = ' | '.join(sep_line)
                            out = input_data
                            counter += 1

    elif ">" in search_arg:  # Evaluate operator
        r_col = search_arg.split(" >")[0]
        search_arg = search_arg.split("> ")[1]
        for line in data:
            line_test = line.split(" | ")
            for x in range(len(line_test)):  # Evaluate each column item
                line_test[x] = line_test[x].split(" ")[0]
                try:
                    line_test[x] = float(line_test[x])  # Check numeric values
                    if line_test[x] > float(search_arg):
                        temp_col = column_index.index(r_col)
                        if x == temp_col:  # Check for column
                            if action == "delete":
                                del input_data[input_data.index(line)]  # Remove matched field
                                out = input_data
                                counter += 1
                            if action == "select":
                                out.append(input_data[input_data.index(line)])
                            if action == "update":
                                print "hi"
                except ValueError:
                    continue
    if flag:
        out = list(set(data) - set(out))
    return counter, out


# Project 2 Specific Functions

def alter_table(input):
    try:
        use_enabled()  # Check that a database is selected
        table_name = input.split("ALTER TABLE ")[1]
        table_name = table_name.split(" ")[0].lower()
        file_name = os.path.join(workingDirectory, table_name)
        if os.path.isfile(file_name):
            if "ADD" in input:  # Only checks for during first project
                with open(file_name, "a") as table:  # Use A to append data to end of the file
                    add_string = input.split("ADD ")[1]
                    table.write(" | " + add_string)
                    print "Table " + table_name + " modified."
        else:
            print "!Failed to alter table " + table_name + " because it does not exist"
    except IndexError:
        print "!Failed to alter Table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def create_db(input):
    try:
        directory = input.split("CREATE DATABASE ")[1]  # Store the string after CREATE DATABASE
        if not os.path.exists(directory):  # Only create it if it doesn't exist
            os.makedirs(directory)
            print "Database " + directory + " created."
        else:
            print "!Failed to create database " + directory + " because it already exists"
    except IndexError:
        print "!Failed to create database because no database name specified"


def create_table(input):
    try:
        use_enabled()  # Check that database is enabled and selected
        sub_dir = re.split("CREATE TABLE ", input, flags=re.IGNORECASE)[1]  # Get a string to use for the table name
        sub_dir = sub_dir.split("(")[0].lower()
        file_name = os.path.join(workingDirectory, sub_dir)
        if not os.path.isfile(file_name):
            with open(file_name, "w") as table:  # Create a file within folder to act as a table
                print "Table " + sub_dir + " created."
                if "(" in input:  # Check for the start of argument section
                    out = []  # Create a list for output to file
                    data = input.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    counter = data.count(",")  # Count num of table arguments
                    for x in range(counter + 1):
                        out.append(data.split(", ")[
                                       x])  # Import args to list for printing
                    table.write(" | ".join(out))  # Output array to the file
        else:
            print "!Failed to create table " + sub_dir + " because it already exists"
    except IndexError:
        print "!Failed to create table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def delete_from(input):
    try:
        use_enabled()  # Check that a database is selected
        table_name = re.split("DELETE FROM ", input, flags=re.IGNORECASE)[1]  # Get a string to use for the table name
        table_name = table_name.split(" ")[0].lower()
        file_name = os.path.join(workingDirectory, table_name)
        if os.path.isfile(file_name):
            with open(file_name, "r+") as table:
                data = table.readlines()
                delete_item = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                counter, out = where(delete_item, "delete", data)
                table.seek(0)
                table.truncate()
                for line in out:
                    table.write(line)
                if counter > 0:
                    print counter, " records deleted."
                else:
                    print "No records deleted."
        else:
            print "!Failed to delete table " + table_name + " because it does not exist"
    except IndexError:
        print "!Failed to delete table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def drop_db(input):
    try:
        directory = input.split("DROP DATABASE ")[1]  # Save string after DROP DATABASE
        if os.path.exists(directory):  # Check db already exists, otherwise can't delete
            for remove_val in os.listdir(directory):  # Empty and remove folder
                os.remove(directory + "/" + remove_val)
            os.rmdir(directory)
            print "Database " + directory + " deleted."
        else:
            print "!Failed to delete database " + directory + " because it does not exist"
    except IndexError:
        print "!No database name specified"


def drop_table(input):
    try:
        use_enabled()  # Check that a database is selected
        sub_dir = input.split("DROP TABLE ")[1].lower()  # Get string to use for the table name
        path_to_table = os.path.join(workingDirectory, sub_dir)
        if os.path.isfile(path_to_table):
            os.remove(path_to_table)
            print "Table " + sub_dir + " deleted."
        else:
            print "!Failed to delete Table " + sub_dir + " because it does not exist"
    except IndexError:
        print "!Failed to remove Table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def insert_into(input):
    try:
        use_enabled()  # Check database is enabled and selected
        table_nm = input.split(" ")[2].lower()  # Get table name
        file_nm = os.path.join(workingDirectory, table_nm)
        if os.path.isfile(file_nm):
            if "values" in input:  # Check for start of argument section
                with open(file_nm, "a") as table:  # Open the file to insert into
                    out = []  # Create list for output to file
                    data = input.split("(", 1)[1]  # Remove (
                    data = data[:-1]  # Remove )
                    counter = data.count(",")  # Count argument number
                    for x in range(counter + 1):
                        out.append(data.split(",")[
                                       x].lstrip())  # Import arguments for printing
                        if "\"" == out[x][0] or "\'" == out[x][0]:
                            out[x] = out[x][1:-1]
                    table.write("\n")
                    table.write(" | ".join(out))  # Output the array to a file
                    print "1 new record inserted."
            else:
                print "!Failed to insert into " + table_nm + " because there were no specified arguments"
        else:
            print "!Failed to alter table " + table_nm + " because it does not exist"
    except IndexError:
        print "!Failed to insert into table because no table name is specified"
    except ValueError as err:
        print err.args[0]


def select_in(command, inputUp):
    try:
        use_enabled()  #Check that a database is selected
        tableName = re.split("FROM ", command, flags=re.IGNORECASE)[1].lower()  #Get string to use for the table name
        if "WHERE" in inputUp:
            tableName = re.split("WHERE", tableName, flags=re.IGNORECASE)[0]
            if " " in tableName:
                tableName = tableName.split(" ")[0]
        fileName = os.path.join(workingDirectory, tableName)
        output = ""
        if os.path.isfile(fileName):
            with open(fileName, "r+") as table:  #Since there should already be tables created, use r+
                if "WHERE" in inputUp: #Using the where to find the matches with all attributes
                    itemToFind = re.split("WHERE ", command, flags=re.IGNORECASE)[1]
                    data = table.readlines()
                    mainCount, output = where(itemToFind,"select",data)
                    for line in output:
                        print line
                if "SELECT *" in inputUp:
                    if not output == "": #Checks if the output is allocated
                        for line in output:
                            print line
                    else:
                        output = table.read()
                        print output
                else: #If doesnt want all attributes, trim down output
                    arguments = re.split("SELECT", command, flags=re.IGNORECASE)[1]
                    attributes = re.split("FROM", arguments, flags=re.IGNORECASE)[0]
                    attributes = attributes.split(",")
                    if not output == "":  #This checks if the output is allocated
                        lines = output
                    else:
                        lines = table.readlines()
                        data = lines
                    for line in lines:
                        out = []
                        for attribute in attributes:
                            attribute = attribute.strip()
                            colIndex = returnColIndex(data)
                            if attribute in colIndex:
                                splitLine = splitLines(line)
                                out.append(splitLine[colIndex.index(attribute)].strip())
                        print " | ".join(out)
        else:
            print "!Failed to query table " + tableName + " because it does not exist"
    except IndexError:
        print "!Failed to select because no table name is specified"
    except ValueError as err:
        print err.args[0]


def join_on(input,inputUp):

    toJoinOn = re.split("on", input, flags=re.IGNORECASE)[1]

    if "INNER" in inputUp:
        return join_where(search_item, table_varibles, data_array)

    if "OUTTER" in inputUp:
        if "LEFT" in inputUp:
            counter, out = where(toJoinOn, "SELECT", data)
            for line in data:
                for matchedData in out:
                    print "hi"
        elif "RIGHT" in inputUp:
            counter, out = where(toJoinOn, "SELECT", data)


def update_from(input):
    try:
        use_enabled()  # Check that a database is selected
        table_nm = re.split("UPDATE ", input, flags=re.IGNORECASE)[1]  # Get string to use for the table name
        table_nm = re.split("SET", table_nm, flags=re.IGNORECASE)[0].lower().strip()
        file_nm = os.path.join(workingDirectory, table_nm)
        if os.path.isfile(file_nm):
            with open(file_nm, "r+") as table:
                data = table.readlines()
                update_item = re.split("WHERE ", input, flags=re.IGNORECASE)[1]
                val = re.split("SET ", input, flags=re.IGNORECASE)[1]
                val = re.split("WHERE ", val, flags=re.IGNORECASE)[0]
                counter, out = where(update_item, "update", data, val)
                table.seek(0)
                table.truncate()
                for line in out:
                    if not "\n" in line:
                        line += "\n"
                    table.write(line)
                if counter > 0:
                    print counter, " records modified."
                else:
                    print "No records modified."
        else:
            print "!Failed to update table " + table_nm + " because it does not exist"
    except IndexError:
        print "!Failed to update table because no table name is specified"
    except ValueError as err:
        print err.args[0]

def transaction(locking_array, lock_flag):

    try:
        fileName = ""
        files = []
        use_enabled()  #Check that a database is selected

        while True:
            clInput = ""

            while not ";" in clInput and not "--" in clInput:
                clInput += raw_input("\n enter a command \n").strip('\r')  #Read clInput command from terminal

            if "commit;" in clInput:
                print locking_array
                break

            clInput = clInput.split(";")[0]  #Remove ; from the clInput command
            inputString = str(clInput)  #Normalize the clInput command

            locking_array.append(inputString)

            if "UPDATE" in inputString.upper():
                table_name = re.split("UPDATE ", locking_array[1], flags=re.IGNORECASE)[1]  #Get string to use for the table name
                table_name = re.split("SET", table_name, flags=re.IGNORECASE)[0].lower().strip()
                file_name = table_name + ".lock"
                files = os.listdir("./locks")
                locking_array[0] = file_name

                path = "./locks/" + file_name
                f = open(path, "w")
                f.close()
                lock_flag = 1

        if file_name in files:
            print "Error: Table", table_name, "is locked!"
            return ["table"], 0

        return locking_array, lock_flag

    except IndexError:
        print "!Something went wrong in 'transaction'"
    except ValueError as err:
        print err.args[0]

def commitHelper(table):
    lockFiles = os.listdir();
    print lockFiles;


def use_db(input):
    try:
        global globalScopeDirectory
        globalScopeDirectory = input.split("USE ")[1]  # Store the string after USE (with global scope)
        if os.path.exists(globalScopeDirectory):
            print "Using database " + globalScopeDirectory + " ."
        else:
            raise ValueError("!Failed to use database because it does not exist")
    except IndexError:
        print "!No database name specified"
    except ValueError as err:
        print err.args[0]


if __name__ == '__main__':
    main()
