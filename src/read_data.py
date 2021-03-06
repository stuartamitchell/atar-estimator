import pandas as pd

def load_data(acs_export_filename, 
            past_params_filename, 
            scaling_groups_filename,
            atar_bounds_filename):
    return (read_acs_export(acs_export_filename), 
            read_past_params(past_params_filename),
            read_scaling_groups(scaling_groups_filename),
            read_atar_bounds(atar_bounds_filename))

def read_acs_export(file):
    '''
    Reads in the Academic Record export from ACS

    Paramters
    ---------
    filename : str
        the location of the export

    Returns
    -------
    list
        a list of students with key data for calculating the ATAR estimate
    '''
    read_df = pd.read_csv(file)
    read_df['Fullname1'] = read_df['Fullname1'].str.rstrip()
    read_df['CoursewithOtherSchool1'] = read_df['CoursewithOtherSchool1'].str.rstrip()

    simplified_df = pd.DataFrame({
            'Student_Id': read_df['StudentId1'],
            'Full_Name': read_df['Fullname1'],
            'Year_Level': read_df['YearLevel1'],
            'Course_Title': read_df['CoursewithOtherSchool1'],
            'Course_Type': read_df['UnitAccredType1'],
            'Unit_Title': read_df['UnitwithOtherCheck1'],
            'Unit_Value': read_df['UnitValue1'],
            'Unit_Score': read_df['ScaledUnitScore1']
    })

    student_names = sorted(list(set([name for name in simplified_df['Full_Name']])))
    students = []

    for name in student_names:
        student_df = simplified_df.loc[simplified_df['Full_Name'] == name]
        split_name = name.split(', ')
        surname = split_name[0]
        given_names = split_name[1]
        student_id = str(student_df.iloc[0]['Student_Id']).rjust(7, '0')

        student = { 'Student_Id': student_id, 'Surname': surname, 'Given_Names': given_names, 'Courses': [] }

        courses = []
        year_level = student_df['Year_Level'].iloc[0]

        for i, row in student_df.iterrows():
            if (row['Course_Title'] not in courses) and ('(' not in row['Course_Title']) and (row['Course_Title'] != 'UNGROUPED UNITS') and (row['Course_Type'] == 'T'):
                courses.append(row['Course_Title'])

        majors = 0
        minors = 0

        for course in courses:
            course_dict = { "Course_Title": course, "Avg_Unit_Score": 0 }
            course_df = student_df.loc[student_df['Course_Title'] == course]

            num_units = len(course_df['Unit_Score'])

            if course in ['SPECIALIST MATHEMATICS', 'SPECIALIST METHODS', 'MATHEMATICAL METHODS', 'MATHEMATICAL APPLIATIONS', 'ENGLISH', 'LITERATURE']:
                course_dict['Major'] = True
                majors = majors + 1
            else:
                if (year_level == 12) and (num_units < 3):
                    course_dict['Major'] = False
                    minors = minors + 1
                elif (year_level == 11) and (num_units < 2):
                    course_dict['Major'] = False
                    minors = minors + 1
                else:
                    course_dict['Major'] = True
                    majors = majors + 1

            unit_scores = [score for score in course_df['Unit_Score'] if score != 0]
            
            if len(unit_scores) > 0:
                course_dict['Avg_Unit_Score'] = round(sum(unit_scores) / len(unit_scores), 2)

            student['Courses'].append(course_dict)
        
        print('Name: ' + name +  ' Majors: ' + str(majors) + ' Minors: ' + str(minors))

        if majors > 2:
            students.append(student)
        
    return students

def read_atar_bounds(file):
    '''
    Reads in the lower bounds for each ATAR point for estimating

    Parameters
    ----------
    filename : str
        the location of the ATAR bounds file

    Returns
    -------
    list
        a list of tuples of the form (lower_bound, ATAR)
    '''
    
    read_df = pd.read_csv(file)
    atar_bounds = []

    for i, row in read_df.iterrows():
        atar_bounds.append((row['LowerBound'], row['ATAR']))
    
    return atar_bounds

def read_past_params(file):
    '''
    Reads in the a and b transforms from a file containing this data for each
    scaling group.

    Parameters
    ----------
    filename : str
        the location of the past parameters file
    
    Returns
    -------
    dict
        a dictionary containing the average a and b transforms for each scaling group
    '''
    read_df = pd.read_csv(file)

    data = {}

    for i, row in read_df.iterrows():
        scaling_group = row['ScalingGroup']

        if scaling_group not in data.keys():
            data[scaling_group] = { 'a': 10, 'b': 2 }
        
        if (row['Parameter'] == 'a'):
            a_list = [a for a in row[2:] if not pd.isna(a)]
            data[scaling_group]['a'] = round(sum(a_list) / len(a_list), 2)
            
        else:
            b_list = [b for b in row[2:] if not pd.isna(b)]
            data[scaling_group]['b'] = round(sum(b_list) / len(b_list), 2)

    return data

def read_scaling_groups(file):
    '''
    Reads in the scaling groups in use at the school from the
    Courses in Scaling Groups report exported from ACS

    Parameters
    ----------
    filename : str
        the location of the scaling groups export from ACS

    Returns
    -------
    dict
        a dict keyed by Course Title, values given by that course's scaling group
    '''
    
    read_df = pd.read_csv(file)

    data = {}

    for i, row in read_df.iterrows():
        if (row['ModGroupType1'] == 'Type T'):
            scaling_group = int(row['Textbox58'].split(' ')[-1])
            course_title = row['CourseTitle']
            data[course_title] = scaling_group
    
    return data
