# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/

# Test
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import mysql.connector
import json
from datetime import datetime
import logging

#MOODLE_ROOT_URL = "https://gtmoodle"
#MOODLE_TOKEN = 'ad0c8f452d7e04ec3e434d685ad138c5'
DB_HOST = "fafaoc.net"
MOODLE_ROOT_URL = "https://gmoodle.eduhk.hk"
MOODLE_TOKEN = 'defaaaa4129b7f1a3c309a0cd5a6b5b9'
#DB_HOST = "gmoodle"


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sender_id = (tracker.current_state())["sender_id"]

        dispatcher.utter_message(text="Hello World!")
        # dispatcher.utter_message(text=(tracker.current_state())["sender_id"])

        mydb = mysql.connector.connect(
            host=DB_HOST,
            user="root",
            password="gmoodle_123",
            database="moodle"
        )

        mydb_cursor = mydb.cursor()
        sql_query = "select id, username, email from mdl_user where username = 'admin';"
        mydb_cursor.execute(sql_query)
        query_result = mydb_cursor.fetchone()

        msg_output = "From db email for admin is : " + query_result[2]
        dispatcher.utter_message(text=msg_output)

        return []


def sql_query_result(sql_query):
    mydb = mysql.connector.connect(
        host=DB_HOST,
        user="root",
        password="gmoodle_123",
        database="moodle"
    )

    mydb_cursor = mydb.cursor()
    mydb_cursor.execute(sql_query)
    query_result = mydb_cursor.fetchall()
    return [list(i) for i in query_result]


def process_incoming_message(tracker):
    # logging.error(json.dumps(tracker.latest_message))
    # sender_id = (tracker.current_state())["sender_id"]
    '''
	events = tracker.current_state()['events']
	user_events = []
	for e in events:
		if e['event'] == 'user':
			user_events.append(e)

	custom_data = user_events[-1]['metadata']
	'''

    intent_detected = tracker.latest_message['intent']
    intent_detected_name = intent_detected['name']
    intent_detected_confidence = intent_detected['confidence']

    intent_ranking = list(tracker.latest_message['intent_ranking'])[0:5]

    # logging.error("sender_id: " + sender_id)
    logging.error(intent_detected)


# logging.error("Intent detected: " + intent_detected_name)
# logging.error("Intent confidence: " + str(intent_detected_confidence))
# logging.error(json.dumps(intent_ranking))
# logging.error("Custom Data:")
# logging.error(custom_data)
# logging.error("course_id: " + course_id)

def get_user_id(tracker):
    try:
        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        custom_data = user_events[-1]['metadata']
        user_id = custom_data['user_id']
    except:
        logging.error("Error in getting user_id")
        return 0
    else:
        return user_id


def get_course_id(tracker):
    try:
        events = tracker.current_state()['events']
        user_events = []
        for e in events:
            if e['event'] == 'user':
                user_events.append(e)

        custom_data = user_events[-1]['metadata']
        course_id = custom_data['course_id']
    except:
        logging.error("Error in getting course_id")
        return 0
    else:
        return course_id


class ActionGetStarted(Action):

    def name(self) -> Text:
        return "action_get_started"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        user_id = get_user_id(tracker)

        buttons = []
        buttons.append({"title": "how many classes did I attend?",
                        "payload": "/gmoodle_class_attendance_enquiry"})
        buttons.append({"title": "how many quizzes in this course?",
                        "payload": "/gmoodle_quiz_count_enquiry"})
        buttons.append({"title": "what are the names of my groupmates?",
                        "payload": "/gmoodle_groupmates_name_enquiry"})

        # dispatcher.utter_message(text="Good morning, how can I help you today?")
        dispatcher.utter_button_message(
            "Good morning, fellas! How can I help you today? Choose any below or type your questions: ",
            buttons)

        return []


class ActionGetClassAttendance(Action):

    def name(self) -> Text:
        return "action_get_class_attendance"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT COUNT(1) as cnt \
					   FROM mdl_role_assignments AS r \
							JOIN mdl_user AS u on r.userid = u.id \
							JOIN mdl_role AS rn on r.roleid = rn.id \
							JOIN mdl_context AS ctx on r.contextid = ctx.id \
							JOIN mdl_course AS c on ctx.instanceid = c.id \
							WHERE rn.shortname = 'student' \
							AND u.id = {}".format(user_id)

        query_result = sql_query_result(sql_query)
        class_attend_cnt = query_result[0][0]

        if (class_attend_cnt <= 1):
            dispatcher.utter_message(
                text="You have attended {} class.".format(class_attend_cnt))
        else:
            dispatcher.utter_message(
                text="You have attended {} classes.".format(class_attend_cnt))
        return []


class ActionGetQuizCount(Action):

    def name(self) -> Text:
        return "action_get_quiz_count"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT COUNT(1) as cnt \
					FROM mdl_quiz q \
					WHERE q.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)
        quiz_cnt = query_result[0][0]

        if (quiz_cnt <= 1):
            dispatcher.utter_message(text="There is {} quiz.".format(quiz_cnt))
        else:
            dispatcher.utter_message(
                text="There are {} quizzes.".format(quiz_cnt))
        return []


class ActionGetQuizDates(Action):

    def name(self) -> Text:
        return "action_get_quiz_dates"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT q.name, IF(q.timeopen>0, q.timeopen, q.timeclose) as time \
					FROM  mdl_quiz q \
					JOIN mdl_modules m ON m.name = \"quiz\" \
					JOIN mdl_course_modules cm ON cm.instance = q.id AND cm.module = m.id \
					WHERE q.course  = {} \
					AND cm.visible = 1".format(course_id)

        query_result = sql_query_result(sql_query)

        quiz_list = []
        caurosel_elements = []
        for x in query_result:
            quiz_list.append(x)
            quiz_name_tmp = x[0]
            quiz_datetime_tmp = datetime.fromtimestamp(x[1]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = quiz_name_tmp
            subtitle_tmp = quiz_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = ""

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Quiz Dates are at...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetAssignmentDeadline(Action):

    def name(self) -> Text:
        return "action_get_assignment_deadline"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					WHERE courseid = {} \
					AND e.visible = 1 AND e.eventtype=\"due\" \
					AND e.modulename=\"assign\" ".format(course_id)

        query_result = sql_query_result(sql_query)

        assignment_list = []
        caurosel_elements = []
        for x in query_result:
            assignment_list.append(x)
            assignment_id_tmp = x[0]
            assignment_name_tmp = x[1]
            assignment_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = assignment_name_tmp
            subtitle_tmp = assignment_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/assign/view.php?id={}".format(
                assignment_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Assignment Deadline are at...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetElearningDates(Action):

    def name(self) -> Text:
        return "action_get_elearning_dates"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					JOIN mdl_tag_instance ti ON ti.itemid = cm.id \
					JOIN mdl_tag t ON t.id = ti.tagid AND t.name = \"online\" \
					WHERE courseid = {} \
					AND e.visible = 1 \
					AND modulename=\"lesson\"".format(course_id)

        query_result = sql_query_result(sql_query)

        elearning_list = []
        caurosel_elements = []
        for x in query_result:
            elearning_list.append(x)
            elearning_id_tmp = x[0]
            elearning_name_tmp = x[1]
            elearning_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = elearning_name_tmp
            subtitle_tmp = elearning_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/lesson/view.php?id={}".format(
                elearning_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="E-learning date are at...")
        dispatcher.utter_message(attachment=output_carousel)
        return []


class ActionGetCourseSchedule(Action):

    def name(self) -> Text:
        return "action_get_course_schedule"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					WHERE courseid = {} \
					AND e.visible = 1 \
					ORDER BY e.timestart".format(course_id)

        query_result = sql_query_result(sql_query)

        schedule_list = []
        caurosel_elements = []
        for x in query_result:
            schedule_list.append(x)
            schedule_id_tmp = x[0]
            schedule_name_tmp = x[1]
            schedule_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = schedule_name_tmp
            subtitle_tmp = schedule_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/assign/view.php?id={}".format(
                schedule_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="This is the course schedule")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetClassActivityLessonN(Action):

    def name(self) -> Text:
        return "action_get_class_activity_lesson_n"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					WHERE courseid = {} \
					AND e.visible = 1 \
					AND DATE(from_unixtime(timestart)) = DATE(now());".format(
            course_id)

        query_result = sql_query_result(sql_query)

        classactivities_list = []
        caurosel_elements = []
        for x in query_result:
            classactivities_list.append(x)
            classactivity_id_tmp = x[0]
            classactivity_name_tmp = x[1]
            classactivity_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = classactivity_name_tmp
            subtitle_tmp = classactivity_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/assign/view.php?id={}".format(
                classactivity_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Class activity today")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetTaskMissedLessonN(Action):

    def name(self) -> Text:
        return "action_get_task_missed_lesson_n"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        lesson_n_value = next(tracker.get_latest_entity_values('CARDINAL'),
                              None)
        if (lesson_n_value is None):
            lesson_n_value = 1

        logging.error("lesson value detected: {}".format(lesson_n_value))

        lesson_n_value_offset = int(lesson_n_value) - 1

        dispatcher.utter_message(
            text="Task missed for lesson {} is...".format(lesson_n_value))
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)

        sql_query = "SELECT cm.id \
                    FROM mdl_course_modules cm \
                    WHERE cm.course = {} \
                    AND section = ( \
                            SELECT section \
                                    FROM mdl_course_modules cm2 \
                            JOIN mdl_modules m ON m.name = \"lesson\" AND m.id = cm2.module \
                            JOIN mdl_lesson l ON l.id = cm2.instance \
                            WHERE cm2.course = cm.course \
                            AND cm2.visible=1 \
                            ORDER BY l.available \
                            LIMIT 1 OFFSET {} \
                    ) \
                    AND cm.id not in ( \
                    SELECT cm_id FROM mdl_eduhk_score es \
                    WHERE es.course_id = cm.course \
                    AND es.user_id ={});".format(course_id, lesson_n_value_offset, user_id)


        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            caurosel_elements = []
            task_missed_section_id_list = []
            for x in query_result:
                task_missed_section_id_list.append(x[0])
            
            print(task_missed_section_id_list)
            cms = get_course_modules(course_id, task_missed_section_id_list)
            print(cms)
            caurosel_elements = get_caurosel_elements_from_cms(cms)

            output_carousel = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": caurosel_elements
                }
            }

            if len(caurosel_elements) == 1:
                dispatcher.utter_message(
                    text="Here is the missed task for lesson {}".format(
                        lesson_n_value))
            else:
                dispatcher.utter_message(
                    text="Here are the missed tasks for lesson {}".format(
                        lesson_n_value))

            dispatcher.utter_message(attachment=output_carousel)

        else:
            dispatcher.utter_message(text="No answer at this moment")


        '''
        if (len(query_result) > 0):
            task_missed_section_id_list = []
            caurosel_elements = []
            for x in query_result:
                task_missed_section_id_list.append(x[0])

            #print(task_missed_list)
            #print(get_course_modules(course_id, task_missed_list))

            task_missed_course_modules_list = get_course_modules(course_id, task_missed_section_id_list)
            print(json.dumps(task_missed_course_modules_list, indent=4))
            for x in task_missed_course_modules_list:
                task_missed_name_tmp = x['name']
                task_missed_url_tmp = x['url']
                title_tmp = task_missed_name_tmp
                subtitle_tmp = ""
                image_url_tmp = ""
                button_title_tmp = "Go to Link"
                button_url_tmp = task_missed_url_tmp

                caurosel_element = {
                    "title": title_tmp,
                    "subtitle": subtitle_tmp,
                    "image_url": image_url_tmp,
                    "buttons": [{
                        "title": button_title_tmp,
                        "url": button_url_tmp,
                        "type": "web_url"
                    }]
                }
                caurosel_elements.append(caurosel_element) 

            output_carousel = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": caurosel_elements
                }
            }

            dispatcher.utter_message(attachment=output_carousel)
        
        
        else:
            dispatcher.utter_message(text="No ans at this moment")
        '''

        return []


class ActionGetClassRank(Action):

    def name(self) -> Text:
        return "action_get_class_rank"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT * FROM ( \
						SELECT user_id, rank() over (order by score desc) as ret_rank FROM( \
						SELECT user_id, SUM(score) as score FROM mdl_eduhk_score \
								WHERE deleted=0 \
								AND course_id = {} \
								GROUP BY user_id \
						) t_sum_score) t_rank \
						WHERE user_id = {}".format(course_id, user_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result)) > 0:
            student_ranking = query_result[0][1]

            dispatcher.utter_message(
                text="You rank {} in the class".format(str(student_ranking)))
        else:
            dispatcher.utter_message(text="No ranking for you in the class")

        return []


class ActionGetGroupmatesName(Action):

    def name(self) -> Text:
        return "action_get_groupmates_name"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT CONCAT(lastname, ' ', firstname) as name, gm.userid \
					FROM mdl_groups_members gm_target_group \
					JOIN mdl_groups_members gm ON gm_target_group.groupid = gm.groupid \
					JOIN mdl_groups g on g.id = gm_target_group.groupid \
					JOIN mdl_user u on u.id = gm.userid \
					WHERE g.courseid = {} \
					AND gm_target_group.userid = {}".format(course_id, user_id)

        query_result = sql_query_result(sql_query)
        groupmate_list = []
        caurosel_elements = []
        for x in query_result:
            groupmate_id_tmp = x[1]
            groupmate_name_tmp = x[0]
            if (groupmate_id_tmp != user_id):
                groupmate_list.append(x)

                title_tmp = groupmate_name_tmp
                subtitle_tmp = ""
                image_url_tmp = "/user/pix.php/{}/f1.jpg".format(
                    str(groupmate_id_tmp))
                button_title_tmp = "Go to Student Profile"
                button_url_tmp = "/user/view.php?id={}&course={}".format(
                    str(groupmate_id_tmp), str(course_id))

                caurosel_element = {
                    "title": title_tmp,
                    "subtitle": subtitle_tmp,
                    "image_url": image_url_tmp,
                    "buttons": [{
                        "title": button_title_tmp,
                        "url": button_url_tmp,
                        "type": "web_url"
                    }]
                }
                caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        # text_separator = " , "
        # dispatcher.utter_message(text="Your groupmates id are {}".format(text_separator.join([str(x) for x in groupmate_list])))
        if (len(caurosel_elements) > 0):
            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="You do not have groupmate")

        return []


class ActionGetFormGroupDeadline(Action):

    def name(self) -> Text:
        return "action_get_formgroup_deadline"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Form group deadline are...")
        try:
            process_incoming_message(tracker)
            course_id = get_course_id(tracker)
            sql_query = "Select timeclose FROM mdl_choicegroup WHERE course={}".format(
                course_id)

            query_result = sql_query_result(sql_query)

            deadline_unixtimestamp = query_result[0][0]
            deadline_dt = datetime.fromtimestamp(
                deadline_unixtimestamp).strftime("%Y-%m-%d %H:%M")
        except:
            dispatcher.utter_message(text="No ans at this moment")
        else:
            dispatcher.utter_message(text=deadline_dt)

        return []


class ActionGetGroupPresentationDatetime(Action):

    def name(self) -> Text:
        return "action_get_group_presentation_datetime"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Group Presentation are at...")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT ss.id, CONVERT(s.name, CHAR), ss.starttime FROM moodle.mdl_scheduler_slots ss \
					JOIN mdl_scheduler_appointment sa ON sa.slotid = ss.id AND sa.studentid = {} \
					JOIN mdl_scheduler s ON s.id = ss.schedulerid \
		            JOIN mdl_modules m ON m.name=\"scheduler\" \
					JOIN mdl_course_modules cm ON cm.instance= s.id AND cm.visible=1 AND cm.course = {} AND m.id = cm.module".format(
            user_id, course_id)

        query_result = sql_query_result(sql_query)

        schedule_list = []
        caurosel_elements = []
        for x in query_result:
            schedule_list.append(x)
            schedule_id_tmp = x[0]
            schedule_name_tmp = x[1]
            # schedule_name_tmp = "testing1234"
            schedule_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = schedule_name_tmp
            subtitle_tmp = schedule_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/scheduler/view.php?id={}".format(
                schedule_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetNextAssignmentDeadline(Action):

    def name(self) -> Text:
        return "action_get_next_assignment_deadline"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					WHERE  e.courseid = {} \
					AND modulename = \"assign\" \
					AND eventtype=\"due\" \
					AND FROM_UNIXTIME(timestart)> NOW() \
					ORDER BY timestart \
					LIMIT 1".format(course_id)

        query_result = sql_query_result(sql_query)

        assignment_list = []
        caurosel_elements = []
        for x in query_result:
            assignment_list.append(x)
            assignment_id_tmp = x[0]
            assignment_name_tmp = x[1]
            assignment_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = assignment_name_tmp
            subtitle_tmp = assignment_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/assign/view.php?id={}".format(
                assignment_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Next Assignment Deadline are at...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetNextWeekLessonDatetime(Action):

    def name(self) -> Text:
        return "action_get_next_week_lesson_datetime"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					WHERE courseid = {} \
					AND modulename=\"lesson\" \
					AND YEARWEEK(NOW(),3)+1 = YEARWEEK(from_unixtime(timestart),3)".format(
            course_id)

        query_result = sql_query_result(sql_query)

        lesson_list = []
        caurosel_elements = []
        for x in query_result:
            lesson_list.append(x)
            lesson_id_tmp = x[0]
            lesson_name_tmp = x[1]
            lesson_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = lesson_name_tmp
            subtitle_tmp = lesson_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/lesson/view.php?id={}".format(lesson_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Next Lesson are at...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetTutorInfo(Action):

    def name(self) -> Text:
        return "action_get_tutor_info"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT CONCAT(u.firstname, \" \", u.lastname) as name, u.id \
					FROM mdl_user u, mdl_role_assignments r, mdl_context cx, mdl_course c, mdl_role role \
					WHERE u.id = r.userid \
					AND r.contextid = cx.id \
					AND cx.instanceid = c.id \
					AND r.roleid = role.id \
					AND role.shortname like (\"%teacher%\") \
					AND cx.contextlevel =50 AND c.id = {} ".format(course_id)

        query_result = sql_query_result(sql_query)

        tutor_list = []
        caurosel_elements = []
        for x in query_result:
            tutor_list.append(x)
            tutor_id_tmp = x[1]
            tutor_name_tmp = x[0]
            title_tmp = tutor_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/user/view.php?id={}&course={}".format(
                tutor_id_tmp, course_id)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Tutor contact is...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetLessonNTopic(Action):

    def name(self) -> Text:
        return "action_get_lesson_n_topic"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)

        lesson_n_value = next(tracker.get_latest_entity_values('CARDINAL'),
                              None)
        if (lesson_n_value is None):
            lesson_n_value = 1

        logging.error("lesson value detected: {}".format(lesson_n_value))

        lesson_n_value_offset = int(lesson_n_value) - 1

        dispatcher.utter_message(
            text="Topic for lesson {} is...".format(lesson_n_value))
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT name FROM mdl_course_sections \
					JOIN ( \
					SELECT cm.id as cm_id FROM mdl_lesson l \
					JOIN mdl_modules m ON m.name = \"lesson\" \
					JOIN mdl_course_modules cm ON l.id = cm.instance AND cm.module = m.id AND cm.visible = 1 AND cm.course={} \
					ORDER BY l.available \
					LIMIT 1 OFFSET {} \
					) tl \
					WHERE sequence LIKE CONCAT(\"%,\", tl.cm_id,\",%\") \
					OR  sequence LIKE CONCAT(tl.cm_id,\",%\") \
					OR sequence LIKE CONCAT(\"%,\", tl.cm_id)".format(course_id,
                                                                      lesson_n_value_offset)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            lesson_topic = query_result[0][0]

            dispatcher.utter_message(text="{}".format(lesson_topic))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


class ActionGetGroupInfo(Action):

    def name(self) -> Text:
        return "action_get_group_info"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Group name is...")
        try:
            process_incoming_message(tracker)
            course_id = get_course_id(tracker)
            user_id = get_user_id(tracker)
            sql_query = "SELECT name FROM moodle.mdl_groups g \
						JOIN mdl_groups_members gm ON g.id = gm.groupid \
						WHERE userid  = {} \
						AND courseid = {}".format(user_id, course_id)

            query_result = sql_query_result(sql_query)

            group_name = query_result[0][0]
        except:
            dispatcher.utter_message(text="No ans at this moment")
        else:
            dispatcher.utter_message(text=group_name)
        return []


'''
class ActionGetGroupmateContact(Action):

	def name(self) -> Text:
		return "action_get_groupmates_contact"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="Your Groupmate contact is...")
		process_incoming_message(tracker)
		return []


class ActionGetCourseGrade(Action):

	def name(self) -> Text:
		return "action_get_course_grade"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="Your grade in this course is...")
		process_incoming_message(tracker)
		return []
'''


class ActionGetCourseDiscussionParticipation(Action):

    def name(self) -> Text:
        return "action_get_course_discussion_participation"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT fd.id as discussion_id, fd.name  FROM moodle.mdl_forum_discussions fd \
					JOIN mdl_groups_members gm ON (fd.groupid = gm.groupid OR fd.groupid = -1) AND gm.userid = {} \
					WHERE fd.course = {} \
					AND fd.id not in ( \
					SELECT distinct(fp.discussion) from mdl_forum_posts fp \
					WHERE fd.userid ={} )".format(user_id, course_id, user_id)

        query_result = sql_query_result(sql_query)

        discussion_list = []
        caurosel_elements = []
        for x in query_result:
            discussion_list.append(x)
            discussion_id_tmp = x[0]
            discussion_name_tmp = x[1]
            title_tmp = discussion_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/forum/discuss.php?d={}".format(
                discussion_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Your discussion participation in this course is...")
        if (len(discussion_list) > 0):
            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="You have finished all discussion")

        return []


'''
class ActionGetMissedTopicDiscussion(Action):

	def name(self) -> Text:
		return "action_get_missed_topic_discussion"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="You missed discussion in following topic...")
		process_incoming_message(tracker)
		return []
'''


class ActionGetCourseLearningResourceUpdate(Action):

    def name(self) -> Text:
        return "action_get_course_learning_resource_update"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT r.name, cm.id  FROM mdl_resource r \
					JOIN mdl_course_modules cm ON r.id = cm.instance \
					JOIN mdl_modules m ON cm.module = m.id AND m.name = \"resource\" \
					WHERE cm.course = {} \
					ORDER BY timemodified DESC".format(course_id)

        query_result = sql_query_result(sql_query)

        resource_list = []
        caurosel_elements = []
        for x in query_result:
            resource_list.append(x)
            resource_id_tmp = x[1]
            resource_name_tmp = x[0]
            title_tmp = resource_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "".format(resource_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Here is the course learning resource update...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetCourseLearningResourceTopicN(Action):

    def name(self) -> Text:
        return "action_get_course_learning_resource_topic_n"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT id as section_id, name, sequence \
                    from mdl_course_sections \
                    WHERE course = {} and visible = 1".format(course_id)

        query_result = sql_query_result(sql_query)

        if(len(query_result) > 0):
            buttons = []
            for x in query_result:
                topic_name_tmp = x[1]
                #print(topic_name_tmp)
                topic_section_id_tmp = x[0]
                topic_sequence_tmp = x[2]
                if(topic_name_tmp is not None):
                    buttons.append({"title": topic_name_tmp,
                                    "payload": "/gmoodle_course_learning_resource_on_specific_topic_enquiry_get_topic_section_id{\"section_id\":"+str(topic_section_id_tmp)+"}"})


            dispatcher.utter_button_message(
                "Which topic do you want to know?",
                buttons)
        else:
            dispatcher.utter_message(text="No ans at this moment")

        return []


class ActionGetCourseLearningResourceBySectionID(Action):

    def name(self) -> Text:
        return "action_get_course_learning_resource_by_section_id"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        course_id = get_course_id(tracker)

        #print(tracker.get_slot('section_id'))

        section_id = tracker.get_slot('section_id')

        cms = get_course_modules_by_section_id(course_id, section_id)
        caurosel_elements = get_caurosel_elements_from_cms(cms)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Here is the course learning resource ...")
        dispatcher.utter_message(attachment=output_carousel)
        return []

'''
class ActionGetCoursePastAverageScore(Action):

	def name(self) -> Text:
		return "action_get_course_past_average_score"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="This course past avg. score is ...")
		process_incoming_message(tracker)
		return []

class ActionGetCoursePastFeedback(Action):

	def name(self) -> Text:
		return "action_get_course_past_feedback"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="This course past avg. feedback score is ...")
		process_incoming_message(tracker)
		return []
'''


class ActionGetAssignmentSubmitMethod(Action):

    def name(self) -> Text:
        return "action_get_assignment_submit_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT cm.id as cm_id, a.name \
					FROM mdl_assign a \
					JOIN mdl_course_modules cm ON a.id = cm.instance AND cm.visible = 1 \
					JOIN mdl_modules m ON cm.module = m.id AND m.name = \"assign\" \
					WHERE cm.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        assignment_list = []
        caurosel_elements = []
        for x in query_result:
            assignment_list.append(x)
            assignment_id_tmp = x[0]
            assignment_name_tmp = x[1]
            title_tmp = assignment_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/assign/view.php?id={}".format(
                assignment_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Please go to the assignment submission pages")
        dispatcher.utter_message(attachment=output_carousel)
        return []


class ActionGetStartDiscussionMethod(Action):

    def name(self) -> Text:
        return "action_get_start_discussion_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT cm.id cm_id, f.name \
					FROM mdl_forum f \
					JOIN mdl_course_modules cm ON f.id = cm.instance AND cm.visible = 1 \
					JOIN mdl_modules m ON m.id = cm.module AND m.name = \"forum\" \
					WHERE cm.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        forum_list = []
        caurosel_elements = []
        for x in query_result:
            forum_list.append(x)
            forum_id_tmp = x[0]
            forum_name_tmp = x[1]
            title_tmp = forum_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "".format(forum_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Here is the list of forum of this course")
        dispatcher.utter_message(attachment=output_carousel)
        dispatcher.utter_message(
            text="You can start the discussion by pressing \'Add a new discussion topic\'")
        return []


class ActionGetReplyDiscussionMethod(Action):

    def name(self) -> Text:
        return "action_get_reply_discussion_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT cm.id cm_id, f.name \
					FROM mdl_forum f \
					JOIN mdl_course_modules cm ON f.id = cm.instance AND cm.visible = 1 \
					JOIN mdl_modules m ON m.id = cm.module AND m.name = \"forum\" \
					WHERE cm.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        forum_list = []
        caurosel_elements = []
        for x in query_result:
            forum_list.append(x)
            forum_id_tmp = x[0]
            forum_name_tmp = x[1]
            title_tmp = forum_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "".format(forum_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Here is the list of forum of this course")
        dispatcher.utter_message(attachment=output_carousel)
        dispatcher.utter_message(
            text="You can reply the discussion by pressing \'Reply\'")
        return []


class ActionGetAssignmentCount(Action):

    def name(self) -> Text:
        return "action_get_assignment_count"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT COUNT(*) as cnt FROM moodle.mdl_assign a \
					JOIN mdl_modules m ON m.name = \"assign\" \
					JOIN mdl_course_modules cm ON cm.instance = a.id AND m.id = cm.module AND cm.visible = 1 \
					WHERE cm.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        assignment_count = query_result[0][0]

        dispatcher.utter_message(text="Number of assignment")
        dispatcher.utter_message(
            text="There is/are {} assignment(s) in this course".format(
                assignment_count))
        return []


class ActionGetReplyDiscussionByMediaMethod(Action):

    def name(self) -> Text:
        return "action_get_reply_discussion_by_media_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="To reply discussion with pic/video, you can...")
        process_incoming_message(tracker)
        return []


class ActionGetAssignmentPctMix(Action):

    def name(self) -> Text:
        return "action_get_assignment_pct_mix"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="The percentage of assignment is...")
        process_incoming_message(tracker)
        return []


class ActionGetOnlineLessonActivity(Action):

    def name(self) -> Text:
        return "action_get_online_lesson_activity"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Here is activity for online lesson...")
        process_incoming_message(tracker)
        return []


class ActionGetLectureNotesPDF(Action):

    def name(self) -> Text:
        return "action_get_lecture_notes_pdf"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT cm.id as cm_id, r.name FROM moodle.mdl_tag_instance ti \
					JOIN mdl_tag t ON ti.tagid = t.id \
					JOIN mdl_course_modules cm ON ti.itemid = cm.id AND ti.itemtype  = \"course_modules\" AND cm.visible =1 \
					JOIN mdl_modules m ON cm.module = m.id AND m.name=\"resource\" \
					JOIN mdl_resource r ON cm.instance = r.id \
					WHERE cm.course = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        material_list = []
        caurosel_elements = []
        for x in query_result:
            material_list.append(x)
            material_id_tmp = x[0]
            material_name_tmp = x[1]
            title_tmp = material_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/mod/resource/view.php?id={}".format(
                material_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="Here is lecture notes pdf...")
        dispatcher.utter_message(attachment=output_carousel)
        return []


class ActionGetTaskCompletion(Action):

    def name(self) -> Text:
        return "action_get_task_completion"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "select (count(distinct(es1.cm_id))/total.total_cm_id) participate_rate from mdl_eduhk_score es1 \
					JOIN (select count(distinct(es2.cm_id)) total_cm_id from mdl_eduhk_score es2 WHERE es2.deleted = 0 AND es2.cm_id > 0 AND es2.course_id > {}) total \
					WHERE es1.deleted = 0 AND es1.cm_id > 0 AND es1.course_id > {} AND es1.user_id > {};".format(
            course_id, course_id, user_id)

        query_result = sql_query_result(sql_query)
        participate_rate = 0
        try:
            participate_rate = query_result[0][0]
        except:
            pass

        dispatcher.utter_message(
            text="Your current contribution score is {0:.1%}. Keep it up!".format(
                participate_rate))

        return []


class ActionGetReplyPostStudent(Action):

    def name(self) -> Text:
        return "action_get_reply_post_student"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Who have replied my post? The answer is...")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT u.id as userid, CONCAT(u.lastname, \" \", u.firstname) as name \
                    FROM mdl_user u \
                    WHERE u.id in ( \
                    SELECT distinct fp.userid \
                    FROM mdl_forum_discussions fd \
                    JOIN mdl_forum_posts fp ON (fp.discussion = fd.id AND fp.userid <> fd.userid) \
                    WHERE fd.userid = {} \
                    AND fd.course = {})".format(user_id, course_id)

        query_result = sql_query_result(sql_query)

        if(len(query_result) > 0):
            user_list = []
            caurosel_elements = []
            for x in query_result:
                user_list.append(x)
                user_id_tmp = x[0]
                user_name_tmp = x[1]
                user_link_url_tmp = "/user/index.php?id={}".format(user_id)
                user_photo_url_tmp = "user/pix.php/{}/f1.jpg".format(user_id)
                title_tmp = user_name_tmp
                subtitle_tmp = ""
                image_url_tmp = user_photo_url_tmp
                button_title_tmp = "Go to Link"
                button_url_tmp = user_link_url_tmp

                caurosel_element = {
                    "title": title_tmp,
                    "subtitle": subtitle_tmp,
                    "image_url": image_url_tmp,
                    "buttons": [{
                        "title": button_title_tmp,
                        "url": button_url_tmp,
                        "type": "web_url"
                    }]
                }
                caurosel_elements.append(caurosel_element)

            output_carousel = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": caurosel_elements
                }
            }

            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No one reply your post")
        return []


class ActionGetLastLessonDatetime(Action):

    def name(self) -> Text:
        return "action_get_last_lesson_datetime"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Last Lesson Date is at...")

        try:
            process_incoming_message(tracker)
            course_id = get_course_id(tracker)
            sql_query = "SELECT  cm.id, e.name, e.timestart FROM moodle.mdl_event e \
						JOIN mdl_modules m ON e.modulename = m.name \
						JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
						WHERE courseid = {} \
						AND modulename=\"lesson\" \
						ORDER BY e.timestart DESC\
						LIMIT 1".format(course_id)

            query_result = sql_query_result(sql_query)

            last_lesson_datetime = datetime.fromtimestamp(
                query_result[0][2]).strftime("%Y-%m-%d %H:%M")
        except:
            dispatcher.utter_message(text="No ans at this moment")
        else:
            dispatcher.utter_message(text=last_lesson_datetime)

        return []


'''
class ActionGetNewTask(Action):

	def name(self) -> Text:
		return "action_get_new_task"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="There are some new task...")
		process_incoming_message(tracker)
		return []
'''


class ActionGetUploadFilesizeMax(Action):

    def name(self) -> Text:
        return "action_get_upload_filesize_max"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="You can upload file is max size...")
        dispatcher.utter_message(text="1GB")
        process_incoming_message(tracker)
        return []


'''
class ActionGetCourseInstructor(Action):

	def name(self) -> Text:
		return "action_get_course_instructor"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="Your course instructor is...Chris")
		process_incoming_message(tracker)
		return []
'''


class ActionGetZoomLink(Action):

    def name(self) -> Text:
        return "action_get_zoom_link"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT cm.id cm_id, l.name, TRIM(Trailing '\"' FROM regexp_substr(l.intro, \"https://.*\\\"\")) link FROM mdl_lesson l \
					JOIN mdl_modules m ON m.name = \"lesson\" \
					JOIN mdl_course_modules cm ON cm.module = m.id AND cm.instance = l.id AND cm.visible=1 AND cm.course = {}\
					JOIN moodle.mdl_tag_instance ti ON ti.itemid = cm.id \
					JOIN mdl_tag t ON ti.tagid = t.id AND t.name=\"online\" \
					WHERE l.available > unix_timestamp(now()) \
					ORDER BY l.available \
					LIMIT 1".format(course_id)

        query_result = sql_query_result(sql_query)

        lesson_list = []
        caurosel_elements = []
        for x in query_result:
            lesson_list.append(x)
            lesson_id_tmp = x[0]
            lesson_name_tmp = x[1]
            lesson_zoom_link_tmp = x[2]
            button_url_tmp = lesson_zoom_link_tmp

            if lesson_zoom_link_tmp == "":
                button_url_tmp = "/mod/lesson/view.php?id={}".format(
                    lesson_id_tmp)

            title_tmp = lesson_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="The zoom link is...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


def get_caurosel_elements_from_cms(cms):
    ret = []
    for cm in cms:
        if "url" not in cm:
            continue
        material_name_tmp = cm["name"]
        material_url_tmp = cm["url"]

        title_tmp = material_name_tmp
        subtitle_tmp = ""
        image_url_tmp = ""
        button_title_tmp = "Go to Link"
        button_url_tmp = material_url_tmp

        caurosel_element = {
            "title": title_tmp,
            "subtitle": subtitle_tmp,
            "image_url": image_url_tmp,
            "buttons": [{
                "title": button_title_tmp,
                "url": button_url_tmp,
                "type": "web_url"
            }]
        }
        ret.append(caurosel_element)
    return ret


class ActionGetLessonMaterial(Action):

    def name(self) -> Text:
        return "action_get_lesson_material"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        lesson_n_value = next(tracker.get_latest_entity_values('CARDINAL'),
                              None)
        if (lesson_n_value is None):
            lesson_n_value = 1

        logging.error("lesson value detected: {}".format(lesson_n_value))

        lesson_n_value_offset = int(lesson_n_value)

        course_id = get_course_id(tracker)

        sql_query = "SELECT section FROM mdl_course_modules cm2 \
					JOIN mdl_modules m ON m.name = \"lesson\" AND m.id = cm2.module \
					JOIN mdl_lesson l ON cm2.instance = l.id \
					WHERE cm2.course = {} \
					AND cm2.visible = 1 \
					ORDER BY l.available \
					LIMIT 1 OFFSET {}".format(course_id,
                                              lesson_n_value_offset - 1)

        query_result = sql_query_result(sql_query)

        if len(query_result) == 0:
            dispatcher.utter_message(text="No answer at this moment")

        section_id = query_result[0][0]

        cms = get_course_modules_by_section_id(course_id, section_id)
        caurosel_elements = get_caurosel_elements_from_cms(cms)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        if (len(caurosel_elements) > 0):
            if len(caurosel_elements) == 1:
                dispatcher.utter_message(
                    text="Here is the material for lesson {}".format(
                        lesson_n_value))
            else:
                dispatcher.utter_message(
                    text="Here are the materials for lesson {}".format(
                        lesson_n_value))

            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No answer at this moment")
        return []


class ActionGetLastLessonMaterial(Action):

    def name(self) -> Text:
        return "action_get_last_lesson_material"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT section FROM mdl_course_modules cm2 \
					JOIN mdl_modules m ON m.name = \"lesson\" AND m.id = cm2.module \
					JOIN mdl_lesson l ON cm2.instance = l.id \
					WHERE cm2.course = {} \
					AND cm2.visible = 1 \
					ORDER BY l.available DESC \
					LIMIT 1 OFFSET 0".format(course_id)

        query_result = sql_query_result(sql_query)

        if len(query_result) == 0:
            dispatcher.utter_message(text="No answer at this moment")

        section_id = query_result[0][0]

        cms = get_course_modules_by_section_id(course_id, section_id)
        caurosel_elements = get_caurosel_elements_from_cms(cms)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        if (len(caurosel_elements) > 0):
            if len(caurosel_elements) == 1:
                dispatcher.utter_message(
                    text="Here is the material for last lesson")
            else:
                dispatcher.utter_message(
                    text="Here are the materials for last lesson")

            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No answer at this moment")
        return []


class ActionGetWikiContributionComparisonWithGroupmate(Action):

    def name(self) -> Text:
        return "action_get_wiki_contribution_comparison_with_groupmate"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT user_id, final_rank, sum_score FROM ( \
					SELECT a.user_id, RANK() OVER (ORDER BY SUM(ws.diff_score)DESC ) final_rank, SUM(ws.diff_score) sum_score \
					FROM mdl_eduhk_wiki_diff_score ws \
					INNER JOIN  mdl_eduhk_score a ON ws.eduhk_score_id = a.id \
					INNER JOIN mdl_groups_members gm ON gm.userid = a.user_id \
					INNER JOIN mdl_groups_members gmt ON gm.groupid = gmt.groupid AND gmt.userid = {} \
					INNER JOIN mdl_groups g on g.id = gm.groupid AND g.courseid = a.course_id \
					WHERE a.course_id = {} \
					AND deleted = 0 \
					GROUP BY a.user_id \
					ORDER BY sum_score DESC \
					) ranking WHERE user_id = {} ;".format(user_id, course_id,
                                                           user_id)

        query_result = sql_query_result(sql_query)

        dispatcher.utter_message(text="Getting Rank for you in your group")
        if (len(query_result) > 0):
            final_rank = query_result[0][1]
            score = query_result[0][2]

            dispatcher.utter_message(
                text="Your contribution score is {}. You are {} in your group. Keep going".format(
                    score, final_rank))
        else:
            dispatcher.utter_message(text="No Rank for you")

        return []


class ActionGetWikiContributionComparisonWithOverall(Action):

    def name(self) -> Text:
        return "action_get_wiki_contribution_comparison_with_overall"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT user_id, final_rank, sum_score FROM ( \
					SELECT a.user_id, RANK() OVER (ORDER BY SUM(ws.diff_score)DESC ) final_rank, SUM(ws.diff_score) sum_score \
					FROM mdl_eduhk_wiki_diff_score ws \
					INNER JOIN  mdl_eduhk_score a ON ws.eduhk_score_id = a.id \
					INNER JOIN mdl_groups_members gm ON gm.userid = a.user_id \
					INNER JOIN mdl_groups g on g.id = gm.groupid AND g.courseid = a.course_id \
					WHERE a.course_id = {} \
					AND deleted = 0 \
					GROUP BY a.user_id \
					ORDER BY sum_score DESC \
					) ranking WHERE user_id = {}".format(course_id, user_id)

        query_result = sql_query_result(sql_query)

        dispatcher.utter_message(text="Getting Rank for you in your class")
        if (len(query_result) > 0):
            final_rank = query_result[0][1]
            score = query_result[0][2]

            dispatcher.utter_message(
                text="Your contribution score is {}. You are {} in your class. Keep going".format(
                    score, final_rank))
        else:
            dispatcher.utter_message(text="No Rank for you")

        return []


'''
class ActionGetForumRaiseQuestionMethod(Action):

	def name(self) -> Text:
		return "action_get_forum_raise_question_method"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="GetForumRaiseQuestionMethod")
		process_incoming_message(tracker)
		return []

class ActionGetForumPostReplyAttachMediaMethod(Action):

	def name(self) -> Text:
		return "action_get_forum_post_reply_attach_method_method"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="GetForumPostReplyAttachMediaMethod")
		process_incoming_message(tracker)
		return []
'''


class ActionGetGroupVacany(Action):

    def name(self) -> Text:
        return "action_get_group_vacany"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT *  FROM moodle.mdl_choicegroup_options cgo \
						JOIN mdl_choicegroup cg ON cgo.choicegroupid = cg.id \
						JOIN mdl_groups g ON cgo.groupid = g.id \
						JOIN mdl_modules m ON m.name =\"choicegroup\" \
						JOIN mdl_course_modules cm ON m.id = cm.module AND cm.instance = cg.id AND cm.visible=1\
						WHERE cg.course = {} \
						AND (cg.limitanswers = 0 \
						OR \
						cgo.maxanswers > ( \
						SELECT COUNT(*) \
						FROM mdl_groups_members gm \
						WHERE gm.groupid = cgo.groupid \
						) ); ".format(course_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            group_list = []
            for x in query_result:
                group_list.append(x[0])

            group_list_join_str = ', '.join(group_list)

            dispatcher.utter_message(text="These group(s) still have vacancies")
            dispatcher.utter_message(text=group_list_join_str)
        else:
            dispatcher.utter_message(text="No group still have vacancies")

        return []


class ActionGetRepliedPostUpdate(Action):

    def name(self) -> Text:
        return "action_get_replied_post_update"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="GetRepliedPostUpdate")
        process_incoming_message(tracker)
        return []


'''
class ActionGetCreatedPostUpdate(Action):

	def name(self) -> Text:
		return "action_get_created_post_update"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="GetCreatedPostUpdate")
		process_incoming_message(tracker)
		return []
'''


class ActionGetGroupRanking(Action):

    def name(self) -> Text:
        return "action_get_group_ranking"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT rank FROM ( \
					SELECT g.id, RANK() over (ORDER BY SUM(score) DESC) as rank,  SUM(score) as score \
					FROM mdl_eduhk_score es \
					JOIN mdl_groups_members gm ON gm.userid = es.user_id \
					JOIN mdl_groups g ON gm.groupid = g.id AND es.course_id = g.courseid \
					WHERE es.course_id = {} \
					GROUP BY g.id \
					) ret JOIN mdl_groups_members gm2 ON gm2.userid = {} AND gm2.groupid = ret.id".format(
            course_id, user_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            rank = query_result[0][0]

            dispatcher.utter_message(text="Your group rank is {}".format(rank))
        else:
            dispatcher.utter_message(
                text="You have no group/your group have no ranking")

        return []


class ActionGetGroupActivePerformance(Action):

    def name(self) -> Text:
        return "action_get_group_active_performance"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Getting most and least active student")
        try:
            process_incoming_message(tracker)
            course_id = get_course_id(tracker)
            user_id = get_user_id(tracker)
            sql_query = "SELECT gm.userid, CONCAT(u.lastname,\" \",u.firstname) name, IF(ISNULL(ret.score), 0, ret.score) score FROM mdl_groups_members gm \
						JOIN mdl_groups_members gm2 ON gm2.groupid = gm.groupid AND gm2.userid = {} \
						LEFT JOIN ( \
						SELECT es.user_id,  SUM(score) as score \
						FROM mdl_eduhk_score es \
						JOIN mdl_groups_members gm ON gm.userid = es.user_id \
						JOIN mdl_groups g ON gm.groupid = g.id AND es.course_id = g.courseid \
						JOIN mdl_groups_members gm2 ON gm2.userid = {} AND gm2.groupid = gm.groupid \
						WHERE es.course_id = {} \
						GROUP BY es.user_id \
						) ret ON ret .user_id = gm.userid \
						JOIN mdl_user u ON gm.userid = u.id \
						ORDER BY score DESC".format(user_id, user_id, course_id)

            query_result = sql_query_result(sql_query)

            most_active_user_name = query_result[0][1]

            sql_query = "SELECT gm.userid, CONCAT(u.lastname," ",u.firstname) name, IF(ISNULL(ret.score), 0, ret.score) score FROM mdl_groups_members gm \
						JOIN mdl_groups_members gm2 ON gm2.groupid = gm.groupid AND gm2.userid = {} \
						LEFT JOIN ( \
						SELECT es.user_id,  SUM(score) as score \
						FROM mdl_eduhk_score es \
						JOIN mdl_groups_members gm ON gm.userid = es.user_id \
						JOIN mdl_groups g ON gm.groupid = g.id AND es.course_id = g.courseid \
						JOIN mdl_groups_members gm2 ON gm2.userid = {} AND gm2.groupid = gm.groupid \
						WHERE es.course_id = {} \
						GROUP BY es.user_id \
						) ret ON ret .user_id = gm.userid \
						JOIN mdl_user u ON gm.userid = u.id \
						ORDER BY score ASC".format(user_id, user_id, course_id)

            query_result = sql_query_result(sql_query)

            least_active_user_name = query_result[0][1]
        except:
            dispatcher.utter_message(text="No ans at this moment")
        else:
            dispatcher.utter_message(
                text="{} is the most active in the group".format(
                    most_active_user_name))
            dispatcher.utter_message(
                text="{} is the least active in the group".format(
                    least_active_user_name))

        return []


class ActionGetMissedResource(Action):

    def name(self) -> Text:
        return "action_get_missed_resource"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetMissedResource")
        process_incoming_message(tracker)
        return []


class ActionGetGroupmateLoginInfo(Action):

    def name(self) -> Text:
        return "action_get_groupmate_login_info"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetGroupmateLoginInfo")
        process_incoming_message(tracker)
        return []


class ActionGetLecturerOffice(Action):

    def name(self) -> Text:
        return "action_get_lecturer_office"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Here is the address and profile of the lectuer")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        sql_query = "SELECT u.id, CONCAT(u.lastname,' ', u.firstname) as name, u.address \
					FROM mdl_role_assignments AS r \
					JOIN mdl_user AS u on r.userid = u.id \
					JOIN mdl_role AS rn on r.roleid = rn.id \
					JOIN mdl_context AS ctx on r.contextid = ctx.id \
					JOIN mdl_course AS c on ctx.instanceid = c.id \
					WHERE rn.shortname like '%teacher' \
					AND c.id = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        office_list = []
        caurosel_elements = []
        for x in query_result:
            office_list.append(x)
            office_id_tmp = x[0]
            office_name_tmp = x[1]
            office_addr_tmp = x[2]
            title_tmp = office_addr_tmp
            subtitle_tmp = office_name_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = "/user/view.php?id={}".format(office_id_tmp)

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        # dispatcher.utter_message(text="Lecturer office is at...")
        dispatcher.utter_message(attachment=output_carousel)

        return []


class ActionGetForumMediaResolutionAdjustmentMethod(Action):

    def name(self) -> Text:
        return "action_get_forum_media_resolution_adjustment_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="After clicking the image/video insert button on moodle, you can edit the size (e.g. 300 x 200), the image/video resolution can be adjusted for better illustration")
        process_incoming_message(tracker)
        return []


class ActionGetChangeProfileMethod(Action):

    def name(self) -> Text:
        return "action_get_change_profile_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Click the top-right corner icon -> select profile -> edit profile")
        process_incoming_message(tracker)
        return []


class ActionGetTopicDifficulties(Action):

    def name(self) -> Text:
        return "action_get_topic_difficulties"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT cs.name,  LENGTH(REGEXP_REPLACE(cs.sequence, '\\d', '')) difficulty, course \
					FROM mdl_course_sections cs \
					WHERE cs.course = {} \
					ORDER BY difficulty DESC \
					LIMIT 1".format(course_id)

        query_result = sql_query_result(sql_query)

        dispatcher.utter_message(text="Most difficult topic is ......")
        if (len(query_result) > 0):
            most_diff_topic_name = query_result[0][0]

            dispatcher.utter_message(text="{}".format(most_diff_topic_name))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


'''
class ActionGetTopicMaterial(Action):

	def name(self) -> Text:
		return "action_get_topic_material"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetTopicMaterial")
		process_incoming_message(tracker)
		return []
'''


class ActionGetClassStudentCount(Action):

    def name(self) -> Text:
        return "action_get_class_student_count"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT count(1) as cnt \
					FROM mdl_role_assignments AS r \
					JOIN mdl_user AS u on r.userid = u.id \
					JOIN mdl_role AS rn on r.roleid = rn.id \
					JOIN mdl_context AS ctx on r.contextid = ctx.id \
					JOIN mdl_course AS c on ctx.instanceid = c.id \
					WHERE rn.shortname = 'student'\
					AND c.id = {}".format(course_id)

        query_result = sql_query_result(sql_query)

        dispatcher.utter_message(
            text="Number of student in this class is ......")
        if (len(query_result) > 0):
            class_student_cnt = query_result[0][0]

            dispatcher.utter_message(text="{}".format(class_student_cnt))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


class ActionGetClassStudentContact(Action):

    def name(self) -> Text:
        return "action_get_class_student_contact"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetClassStudentContact")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)

        dispatcher.utter_message(
            text="You can check the student information [here](/user/index.php?id={})".format(
                course_id))

        return []


'''
class ActionGetClassStudentMajorDistribution(Action):

	def name(self) -> Text:
		return "action_get_class_student_major_distribution"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetClassStudentMajorDistribution")
		process_incoming_message(tracker)
		return []
'''


class ActionGetFreqQuestionAsked(Action):

    def name(self) -> Text:
        return "action_get_freq_question_asked"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetFreqQuestionAsked")
        process_incoming_message(tracker)
        return []


'''
class ActionGetContentDisplayProblemSolution(Action):

	def name(self) -> Text:
		return "action_get_content_display_problem_solution"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetContentDisplayProblemSolution")
		process_incoming_message(tracker)
		return []

class ActionGetVideoDisplayProblemSolution(Action):

	def name(self) -> Text:
		return "action_get_video_display_problem_solution"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetVideoDisplayProblemSolution")
		process_incoming_message(tracker)
		return []
'''


class ActionGetLectureTime(Action):

    def name(self) -> Text:
        return "action_get_lecture_time"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT cm.id cm_id, l.name, l.available as timetimp FROM mdl_lesson l \
					JOIN mdl_modules m ON m.name = \"lesson\" \
					JOIN mdl_course_modules cm ON cm.module = m.id AND cm.instance = l.id AND cm.visible=1 \
					JOIN moodle.mdl_tag_instance ti ON ti.itemid = cm.id \
					JOIN mdl_tag t ON ti.tagid = t.id AND t.name=\"online\" \
					WHERE l.available > unix_timestamp(now()) \
					AND cm.course = {} \
					ORDER BY l.available \
					LIMIT 1;".format(course_id)

        query_result = sql_query_result(sql_query)

        lecture_list = []
        caurosel_elements = []
        for x in query_result:
            lecture_list.append(x)
            lecture_id_tmp = x[0]
            lecture_name_tmp = x[1]
            lecture_datetime_tmp = datetime.fromtimestamp(x[2]).strftime(
                "%Y-%m-%d %H:%M")
            title_tmp = lecture_name_tmp
            subtitle_tmp = lecture_datetime_tmp
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = ""

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="The lecture time is...")
        if (len(lecture_list) > 0):
            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


'''
class ActionGetLastLectureDatetime(Action):

	def name(self) -> Text:
		return "action_get_last_lecture_datetime"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetLastLectureDatetime")
		process_incoming_message(tracker)
		return []
'''


class ActionGetCourseImportantDate(Action):

    def name(self) -> Text:
        return "action_get_course_important_date"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT cm.id, e.name, e.timestart, CONCAT(\"/mod/\", e.modulename,\"/view.php?id=\", cm.id)  url FROM moodle.mdl_event e \
					JOIN mdl_modules m ON e.modulename = m.name \
					JOIN mdl_course_modules cm ON e.instance = cm.instance AND cm.module = m.id AND cm.course = e.courseid \
					JOIN mdl_role_assignments AS r ON r.userid = {} \
					JOIN mdl_user AS u on r.userid = u.id \
					JOIN mdl_role AS rn on r.roleid = rn.id \
					JOIN mdl_context AS ctx on r.contextid = ctx.id \
					JOIN mdl_course AS c on ctx.instanceid = c.id AND c.id = cm.course \
					WHERE e.visible = 1 \
					AND MONTH(from_unixtime(e.timestart)) = MONTH(NOW());".format(
            user_id)

        query_result = sql_query_result(sql_query)

        event_list = []
        caurosel_elements = []
        for x in query_result:
            event_list.append(x)
            event_id_tmp = x[0]
            event_name_tmp = x[1]
            event_url_tmp = x[3]
            title_tmp = event_name_tmp
            subtitle_tmp = ""
            image_url_tmp = ""
            button_title_tmp = "Go to Link"
            button_url_tmp = event_url_tmp

            caurosel_element = {
                "title": title_tmp,
                "subtitle": subtitle_tmp,
                "image_url": image_url_tmp,
                "buttons": [{
                    "title": button_title_tmp,
                    "url": button_url_tmp,
                    "type": "web_url"
                }]
            }
            caurosel_elements.append(caurosel_element)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(text="The course important dates is...")
        if (len(event_list) > 0):
            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


class ActionGetSemesterLastday(Action):

    def name(self) -> Text:
        return "action_get_semester_lastday"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetSemesterLastday")
        process_incoming_message(tracker)
        return []


class ActionGetPostReplyBySpecificStudentCount(Action):

    def name(self) -> Text:
        return "action_get_post_reply_by_specific_student_count"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="ActionGetPostReplyBySpecificStudentCount")
        process_incoming_message(tracker)
        return []


class ActionGetPostReplyBySpecificStudent(Action):

    def name(self) -> Text:
        return "action_get_post_reply_by_specific_student"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetPostReplyBySpecificStudent")
        process_incoming_message(tracker)
        return []


class ActionGetStudentContact(Action):

    def name(self) -> Text:
        return "action_get_student_contact"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetStudentContact")
        process_incoming_message(tracker)
        return []


'''
class ActionGetCourseMaterial(Action):

	def name(self) -> Text:
		return "action_get_course_material"

	def run(self, dispatcher: CollectingDispatcher,
			tracker: Tracker,
			domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

		dispatcher.utter_message(text="ActionGetCourseMaterial")
		process_incoming_message(tracker)
		return []
'''


class ActionGetClassActivityCountHighest(Action):

    def name(self) -> Text:
        return "action_get_class_activity_count_highest"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT es.user_id, COUNT(*) no_activity \
						FROM mdl_eduhk_score es \
						WHERE es.course_id = {} \
						GROUP BY es.user_id \
						ORDER BY no_activity DESC \
						LIMIT 1 ".format(course_id)

        query_result = sql_query_result(sql_query)

        dispatcher.utter_message(
            text="Accumulated No. of activities of class is ......")
        if (len(query_result) > 0):
            activities_cnt = query_result[0][0]

            dispatcher.utter_message(text="{}".format(activities_cnt))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


class ActionGetAssignmentGrade(Action):

    def name(self) -> Text:
        return "action_get_assignment_grade"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="ActionGetAssignmentGrade")
        process_incoming_message(tracker)
        assignment_n_value = next(tracker.get_latest_entity_values('CARDINAL'),
                                  None)
        if (assignment_n_value is None):
            assignment_n_value = 1

        logging.error(
            "assignment value detected: {}".format(assignment_n_value))

        assignment_n_value_offset = int(assignment_n_value) - 1

        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT ag.grade FROM mdl_assign_grades ag \
					JOIN (SELECT a.id, a.name, a.course FROM mdl_assign a \
					JOIN mdl_modules m ON m.name = \"assign\" \
					JOIN mdl_course_modules cm ON cm.module = m.id AND cm.instance = a.id AND cm.visible = 1 \
					WHERE a.course = {} ORDER BY a.duedate LIMIT 1  OFFSET {}) a \
					ON a.id = ag.assignment \
					WHERE  ag.userid = {}".format(course_id,
                                                  assignment_n_value_offset,
                                                  user_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            grade = query_result[0][0]

            dispatcher.utter_message(
                text="Your grading for assignment {} is: {}".format(
                    assignment_n_value, grade))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []


class ActionGetWeeklyPerformance(Action):

    def name(self) -> Text:
        return "action_get_weekly_performace"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="ActionGetWeeklyPerformance")
        process_incoming_message(tracker)
        return []


class ActionGetChangePasswordMethod(Action):

    def name(self) -> Text:
        return "action_get_change_password_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Click your name at the top right corner > choose \"Preferences\" > click \"Change Password\"")
        process_incoming_message(tracker)
        return []

class ActionGetGroupmateGroupN(Action):

    def name(self) -> Text:
        return "action_get_groupmate_group_N"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(
            text="Groupmate for Group N are...")
        process_incoming_message(tracker)

        group_n_value = next(tracker.get_latest_entity_values('CARDINAL'),
                              None)
        if (group_n_value is None):
            group_n_value = 1

        logging.error("Group value detected: {}".format(group_n_value))

        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)

        sql_query = "SELECT u.id as user_id, CONCAT(u.lastname, \" \", u.firstname) as name \
                    FROM mdl_groups_members gm \
                    JOIN mdl_user u ON gm.userid = u.id \
                    WHERE gm.groupid  = ( \
                    SELECT g.id \
                    FROM mdl_groups g \
                    WHERE regexp_substr(g.name, \"(\\\d+)\") = \'{}\' \
                    AND g.courseid ={})".format(group_n_value, course_id)

        print(sql_query)
        query_result = sql_query_result(sql_query)
        print(query_result)


        if (len(query_result) > 0):
            caurosel_elements = []
            groupmate_list = []
            for x in query_result:
                groupmate_list.append(x)
                groupmate_id_tmp = x[0]
                groupmate_name_tmp = x[1]
                groupmate_link_url_tmp = "/user/index.php?id={}".format(groupmate_id_tmp)
                groupmate_photo_url_tmp = "/user/pix.php/{}/f1.jpg".format(groupmate_id_tmp)
                title_tmp = groupmate_name_tmp
                subtitle_tmp = ""
                image_url_tmp = groupmate_photo_url_tmp
                button_title_tmp = "Go to Link"
                button_url_tmp = groupmate_link_url_tmp

                caurosel_element = {
                    "title": title_tmp,
                    "subtitle": subtitle_tmp,
                    "image_url": image_url_tmp,
                    "buttons": [{
                        "title": button_title_tmp,
                        "url": button_url_tmp,
                        "type": "web_url"
                    }]
                }
                caurosel_elements.append(caurosel_element)

            output_carousel = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": caurosel_elements
                }
            }

            dispatcher.utter_message(attachment=output_carousel)

        else:
            dispatcher.utter_message(text="No answer at this moment")

        return []

class ActionGetContributionScore(Action):

    def name(self) -> Text:
        return "action_get_current_contribution_score"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="ActionGetContributionScore")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT SUM(score) \
                    FROM mdl_eduhk_score es \
                    WHERE es.deleted = 0 \
                    AND user_id = {} \
                    AND course_id = {}".format(user_id, course_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            score = query_result[0][0]

            dispatcher.utter_message(
                text="Your current contribution score is {}. ".format(score))
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []

class ActionGetGroupAllocationMethod(Action):

    def name(self) -> Text:
        return "action_get_group_allocation_method"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="ActionGetGroupAllocationMethod")
        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)
        sql_query = "SELECT cm.id as cm_id, cg.name \
                    FROM mdl_choicegroup cg \
                    JOIN mdl_modules m ON m.name = \"choicegroup\" \
                    JOIN mdl_course_modules cm ON cm.module = m.id AND cm.instance = cg.id \
                    WHERE cg.course = {} ".format(course_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            caurosel_elements = []
            group_list = []
            for x in query_result:
                group_list.append(x)
                group_id_tmp = x[0]
                group_name_tmp = x[1]
                group_link_url_tmp = "/mod/choicegroup/view.php?id={}".format(group_id_tmp)
                title_tmp = group_name_tmp
                subtitle_tmp = ""
                image_url_tmp = ""
                button_title_tmp = "Go to Link"
                button_url_tmp = group_link_url_tmp

                caurosel_element = {
                    "title": title_tmp,
                    "subtitle": subtitle_tmp,
                    "image_url": image_url_tmp,
                    "buttons": [{
                        "title": button_title_tmp,
                        "url": button_url_tmp,
                        "type": "web_url"
                    }]
                }
                caurosel_elements.append(caurosel_element)

            output_carousel = {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": caurosel_elements
                }
            }

            dispatcher.utter_message(attachment=output_carousel)
        else:
            dispatcher.utter_message(text="No ans at this moment")
        return []

class ActionGetMaterialRecommendation(Action):

    def name(self) -> Text:
        return "action_get_material_recommendation"

    @classmethod
    def get_recommendation_rule_json(cls, course_id):
        sql_query = "select * from mdl_eduhk_chatbot_rules where course_id = {}".format(
            course_id)
        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            course_recommendation_json = query_result[0][2]
            return course_recommendation_json
        else:
            return -1

    @classmethod
    def get_user_reading_count(cls, user_id, course_id):
        sql_query = "SELECT COUNT(distinct(cm.id)) as reading_cnt FROM moodle.mdl_eduhk_score es \
					JOIN mdl_course_modules cm ON es.cm_id = cm.id \
					JOIN mdl_modules m ON cm.module = m.id \
					WHERE m.name in (\"url\", \"resource\") \
					AND es.course_id = {} \
					AND es.user_id = {}".format(course_id, user_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            reading_count = query_result[0][0]
            return reading_count
        else:
            logging.error(
                "Error in getting reading count for user {} in course {}".format(
                    str(user_id), str(course_id)))
            return -1

    @classmethod
    def get_user_quiz_grade(cls, user_id, course_oid):
        sql_query = "select d.grade \
					from mdl_course_modules a \
					left join mdl_modules b on a.module = b.id \
					left join mdl_quiz c on a.instance = c.id \
					left join mdl_quiz_grades d on c.id = d.quiz and a.instance = d.quiz \
					where a.id = {} \
					and d.userid = {}".format(course_oid, user_id)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            quiz_grade = query_result[0][0]
            return quiz_grade
        else:
            logging.error(
                "Error in getting quiz grade for user {} in course oid {}".format(
                    str(user_id), str(course_oid)))
            return -1

    @classmethod
    def eval_recommendation_comparison(cls, op, l_result, r_result):
        if (op in ["and", "or"] and l_result in [True, False] and r_result in [
            True, False]):
            if (op == "and"):
                return l_result and r_result
            else:
                return l_result or r_result
        else:
            return False

    @classmethod
    def eval_recommendation_clause_op_null(cls, value, check_op, check_value):
        if (value == -1):
            return False

        if (check_op == "is_finish"):
            return value > 0
        elif (check_op == "score_less"):
            return value < check_value
        elif (check_op == "score_more"):
            return value > check_value
        elif (check_op == "score_eq"):
            return value == check_value
        else:
            return False

    @classmethod
    def eval_recommendation_clause(cls, recommendation_clause, user_id,
        course_id):
        # logging.error(recommendation_if_clause)
        try:
            recommendation_clause["check_value"] = float(recommendation_clause["check_value"])
        except:
            return False

        recommendation_op = recommendation_clause["op"]
        if (recommendation_op is None):
            # logging.error("recommendation_op is null")
            if (recommendation_clause["oid"].lstrip('-').isdigit() == False):
                logging.error("Error in oid")
                return False
            oid = int(recommendation_clause["oid"])
            check_op = recommendation_clause["check_op"]
            check_value = recommendation_clause["check_value"]

            if (not (oid == -1 or oid > 0)):
                logging.error("Error in oid")
                return False

            if (check_op not in ["is_finish", "score_less", "score_more",
                                 "score_eq"]):
                logging.error("Error in check_op")
                return False

            if (oid == -1):
                # reading count
                reading_count = cls.get_user_reading_count(user_id, course_id)
                return cls.eval_recommendation_clause_op_null(reading_count,
                                                               check_op,
                                                               check_value)
            elif (oid > 0):
                # Quiz
                quiz_grade = cls.get_user_quiz_grade(user_id, oid)
                return cls.eval_recommendation_clause_op_null(quiz_grade,
                                                               check_op,
                                                               int(check_value))
            else:
                return False


        else:
            l_result = cls.eval_recommendation_clause(
                recommendation_clause["l"], user_id, course_id)
            r_result = cls.eval_recommendation_clause(
                recommendation_clause["r"], user_id, course_id)
            return (
                cls.eval_recommendation_comparison(recommendation_op, l_result,
                                                    r_result))
    @classmethod
    def get_course_oid_module_type(cls, oid):
        sql_query = "select b.name \
					from mdl_course_modules a \
					left join mdl_modules b on a.module = b.id \
					where a.id = {}".format(oid)

        query_result = sql_query_result(sql_query)

        if (len(query_result) > 0):
            module_type = query_result[0][0]
            return module_type
        else:
            logging.error(
                "Error in getting module type for course oid {}".format(oid))
            return None

    @classmethod
    def get_course_oid_name(cls, oid, module_type):
        sql_query = "select c.name as name \
					from mdl_course_modules a \
					left join mdl_modules b on a.module = b.id \
					left join mdl_{} c on a.instance = c.id \
					where a.id = {}".format(module_type, oid)

        try:
            query_result = sql_query_result(sql_query)
        except:
            logging.error(
                "Error in getting module_name for course oid {}".format(oid))
            return None
        else:
            if (len(query_result) > 0):
                module_name = query_result[0][0]
                return module_name
            else:
                logging.error(
                    "Error in getting module_name for course oid {}".format(
                        oid))
                return None

    @classmethod
    def get_carousel_recommendation_by_user_course_id(cls, user_id:int, course_id:int) -> List:
        caurosel_elements = []
        # buttons = []

        course_recommendation_json_str = cls.get_recommendation_rule_json(
            course_id)


        if (course_recommendation_json_str == -1):
            return []

        # Extract json
        course_recommendation_json = json.loads(course_recommendation_json_str)
        # logging.error(course_recommendation_json)
        # logging.error(len(course_recommendation_json))
        course_recommendation_json_tmp = course_recommendation_json[0]
        for course_recommendation_json_tmp in course_recommendation_json:
            course_recommendation_json_tmp_if_clause = \
                course_recommendation_json_tmp["if"]
            course_recommendation_json_tmp_then_clause = \
                course_recommendation_json_tmp["then"]
            course_recommendation_json_tmp_if_clause_eval_result = cls.eval_recommendation_clause(
                course_recommendation_json_tmp_if_clause, user_id, course_id)
            logging.error("User meet recommendation requirement: {}".format(
                cls.eval_recommendation_clause(
                    course_recommendation_json_tmp_if_clause, user_id,
                    course_id)))
            if (course_recommendation_json_tmp_if_clause_eval_result == True):
                for course_oid_tmp in course_recommendation_json_tmp_then_clause:
                    if (course_oid_tmp.isdigit() == True):
                        course_oid_tmp_int = int(course_oid_tmp)
                        course_oid_tmp_module_type = cls.get_course_oid_module_type(
                            course_oid_tmp_int)
                        if (not (course_oid_tmp_module_type is None)):
                            course_oid_tmp_module_name = cls.get_course_oid_name(
                                course_oid_tmp, course_oid_tmp_module_type)
                            if (not (course_oid_tmp_module_name is None)):
                                recommendation_name = course_oid_tmp_module_name
                                recommendation_type = course_oid_tmp_module_type
                                recommendation_link_url = "/mod/{}/view.php?id={}".format(
                                    recommendation_type, course_oid_tmp_int)

                                caurosel_element = {
                                    "title": recommendation_name,
                                    # "image_url": "https://cdn.lihkg.com/assets/img/icon.png",
                                    "image_url": "",
                                    "buttons": [{
                                        "title": "Go to Link url",
                                        "url": recommendation_link_url,
                                        "type": "web_url"
                                    }]
                                }
                                caurosel_elements.append(caurosel_element)

                                '''
                                button = {
                                            "title": recommendation_name,
                                            "payload": recommendation_link_url
                                         }

                                buttons.append(button)
                                '''



        return caurosel_elements

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        user_id = get_user_id(tracker)
        course_id = get_course_id(tracker)

        caurosel_elements = self.get_carousel_recommendation_by_user_course_id(user_id, course_id)

        output_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }

        dispatcher.utter_message(
            text="Nothing is better than reading and gaining more and more knowledge! I am glad that you are taking initiatives to learn more! Here is the reading list that your tutor and I suggest for this course. ")

        if (len(caurosel_elements) > 0):
            dispatcher.utter_message(attachment=output_carousel)
        # dispatcher.utter_button_message("Here is your recommendation", buttons)
        else:
            dispatcher.utter_message(text="No Recommendation at this moment")

        return []


class ActionGetCustomdata(Action):

    def name(self) -> Text:
        return "action_get_customdata"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)
        user_id = get_user_id(tracker)

        '''
		events = tracker.current_state()['events']
		user_events = []
		for e in events:
			if e['event'] == 'user':
				user_events.append(e)

		custom_data = user_events[-1]['metadata']
		#custom_data_json_load = json.loads(custom_data)

		if ('user_id' in custom_data):
			user_id = custom_data['user_id']
		else:
			user_id = ''

		if ('course_id' in custom_data):
			course_id = custom_data['course_id']
		else:
			course_id = ''
		'''

        dispatcher.utter_message(text="Get Custom Data")
        dispatcher.utter_message(text="user_id: {}".format(user_id))
        dispatcher.utter_message(text="course_id: {}".format(course_id))

        return []


def get_caurosel_dispatch_message(caurosel_elements:List):
    return {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": caurosel_elements
            }
        }


def get_course_outline(course_id:int):

    sql = "SELECT cm.id as cm_id FROM moodle.mdl_tag_instance ti " \
          "JOIN mdl_tag t ON ti.tagid = t.id AND t.name=\"courseinformation\"" \
          "JOIN mdl_course_modules cm ON ti.itemid = cm.id AND ti.itemtype  = \"course_modules\" AND cm.visible =1 " \
          "WHERE cm.course = {}".format(course_id)

    sql_ret = sql_query_result(sql)
    cm_ids = []
    for row in sql_ret:
        cm_ids.append(row[0])

    return get_course_modules(course_id, cm_ids=cm_ids)


class ActionGetCourseOutline(Action):

    def name(self) -> Text:
        return "action_get_course_outline"

    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        process_incoming_message(tracker)
        course_id = get_course_id(tracker)

        cms = get_course_outline(course_id)

        dispatcher.utter_message(attachment=get_caurosel_dispatch_message(get_caurosel_elements_from_cms(cms)))


def get_course_modules_by_section_id(course_id, section_id):
    ret = []
    response = requst_sections_with_course_modules(course_id, section_id)
    if len(response) == 0:
        return ret
    cms = response[0]["modules"]
    for cm in cms:
        if cm["visible"] == 1:
            ret.append(cm)
    return ret


def get_course_modules(course_id, cm_ids: List[int]):
    r = request_course_modules(course_id)

    cms = json.loads(r.text)

    ret = []
    # trans the section and cm
    for section in cms:
        for cm in section["modules"]:
            if cm["id"] in cm_ids and cm["visible"] == 1:
                ret.append(cm)

    return ret


def requst_sections_with_course_modules(course_id, section_id):
    options = {
        "options[0][name]": "sectionid",
        "options[0][value]": section_id,
    }

    r = request_course_modules(course_id, options)

    cms = json.loads(r.text)

    return cms


def request_course_modules(course_id: int, options: Dict = {}):
    target = '{}/webservice/rest/server.php?'.format(MOODLE_ROOT_URL)
    moodle_create_token = MOODLE_TOKEN
    url_payload = {
        "wstoken": moodle_create_token,
        "wsfunction": "core_course_get_contents",
        "moodlewsrestformat": "json",
        "courseid": course_id,
    }

    url_payload.update(options)

    r = requests.get(target, params=url_payload, verify=False)

    return r


if __name__ == '__main__':
    ActionGetMaterialRecommendation.get_carousel_recommendation_by_user_course_id(1,27)
