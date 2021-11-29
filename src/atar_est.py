import pandas as pd

def calculate_aggregate_score(student, past_params, scaling_groups):
    '''
    Calculates the aggregate score for a student

    Parameters
    ----------
    student : dict
        a dict containing student data
    past_params : dict
        a dict containing the scaling parameters for each scaling group
    scaling_groups : dict
        a dict containing the scaling group for each course

    Returns
    -------
    (dict, int)
        a tuple containing the student's best four courses and the aggregate score rounded to the nearest integer
    '''
    majors = [course for course in student['Courses'] if course['Major'] == True]
    minors = [course for course in student['Courses'] if course['Major'] == False]

    if len(majors) < 3:
        return 0
    else:
        majors.sort(key=lambda m: m['Avg_Unit_Score'], reverse=True)
        best_three = majors[0:3]

        if len(majors) > 3:
            choices_for_fourth = majors[3:] + minors
        else:
            choices_for_fourth = minors

        choices_for_fourth.sort(key=lambda m: m['Avg_Unit_Score'], reverse=True)
        fourth = choices_for_fourth[0]
        best_four = best_three + [fourth]

        scaled_scores = []

        for course in best_four:
            scaling_group = scaling_groups[course['Course_Title']]
            scaled_score = course['Avg_Unit_Score'] * past_params[scaling_group]['b'] + past_params[scaling_group]['a']
            scaled_scores.append(scaled_score)

        courses = {}

        courses['Major1'] = best_four[0]['Course_Title']
        courses['Major2'] = best_four[1]['Course_Title']
        courses['Major3'] = best_four[2]['Course_Title']
        courses['Minor'] = best_four[3]['Course_Title']

        aggregate_score = int(round(scaled_scores[0] + scaled_scores[1] + scaled_scores[2] + 0.6 * scaled_scores[3], 0))

        return courses, aggregate_score
    
def predict_atar(aggregate_score, atar_bounds):
    '''
    Predicts an ATAR given an aggregate score and a list of lower bounds

    Parameters
    ----------
    aggregate_score : int
        a student's aggregate score rounded to the nearest integer
    
    atar_bounds : list
        a list of tuples of the form (lower_bound, atar)
    '''
    for lower, atar in atar_bounds:
        if aggregate_score >= lower:
            return atar

def predicted_atar_range(predicted_atar):
    '''
    Creates a string with the predicted ATAR range as a 10 point range

    Parameters
    ----------
    predicted_atar : int
        the student's predicted ATAR to the nearest int
    
    Returns
    -------
    str
        a string containing the ten point ATAR range
    '''
    if predicted_atar > 96:
        return "90 - 100"
    else:
        return str(predicted_atar - 7) + " - " + str(predicted_atar + 3)

def produce_atar_estimates(students, past_params, scaling_groups, atar_bounds):
    '''
    Produces the students predicted ATAR and ATAR range and stores it in a dataframe

    Parameters
    ----------
    students : list
        a list containing the student data

    Returns
    -------
    dataframe
        a dataframe containing the students' names, predicted ATAR, and ATAR range
    '''
    student_predictions = []

    for student in students:
        courses, aggregate_score = calculate_aggregate_score(student, past_params, scaling_groups)
        atar_prediction = predict_atar(aggregate_score, atar_bounds)
        atar_range = predicted_atar_range(atar_prediction)
        student_predictions.append({
                                    'Student_Id': student['Student_Id'], 
                                    'Full_Name': student['Full_Name'], 
                                    'ATAR_Prediction': atar_prediction,
                                    'Predicted_Range': atar_range,
                                    'Major1': courses['Major1'],
                                    'Major2': courses['Major2'],
                                    'Major3': courses['Major3'],
                                    'Minor': courses['Minor']
                                })
    
    return pd.DataFrame(student_predictions)