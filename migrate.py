import json
import mysql.connector
import pymongo
from datetime import datetime
from bson import ObjectId
import re

class LearnDashToOpenEdx:
    def __init__(self, mysql_config, mongo_uri):
        """
        Initialize connections to MySQL and MongoDB
        """
        self.mysql_conn = mysql.connector.connect(**mysql_config)
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.db = self.mongo_client.openedx
        self.definitions = self.db.modulestore.definitions
        self.structures = self.db.modulestore.structures

    def sanitize_content(self, content):
        """
        Clean HTML content and prepare it for OpenEdX
        """
        if not content:
            return ""
        # Remove WordPress shortcodes
        content = re.sub(r'\[[^\]]+\]', '', content)
        # Basic HTML cleanup
        content = content.replace('\\', '\\\\').replace('"', '\\"')
        return content

    def generate_block_id(self, block_type, display_name):
        """
        Generate a block ID similar to OpenEdX format
        """
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', display_name.lower())
        return f"{block_type}+block@{safe_name}_{str(ObjectId())[:8]}"

    def transform_topic(self, topic_data):
        """
        Transform LearnDash topic to OpenEdX vertical
        """
        definition_id = ObjectId()
        block_id = self.generate_block_id("vertical", topic_data['display_name'])
        
        html_block_id = self.generate_block_id("html", f"{topic_data['display_name']}_content")
        html_definition = {
            "_id": ObjectId(),
            "block_type": "html",
            "definition_data": {
                "data": self.sanitize_content(topic_data['definition_data']),
                "display_name": f"{topic_data['display_name']} Content"
            }
        }
        
        definition = {
            "_id": definition_id,
            "block_type": "vertical",
            "definition_data": {
                "display_name": topic_data['display_name']
            }
        }
        
        return {
            "block_id": block_id,
            "definition": definition,
            "html_block": {
                "block_id": html_block_id,
                "definition": html_definition
            },
            "block_type": "vertical",
            "fields": {
                "display_name": topic_data['display_name']
            }
        }

    def transform_lesson(self, lesson_data):
        """
        Transform LearnDash lesson to OpenEdX sequential
        """
        definition_id = ObjectId()
        block_id = self.generate_block_id("sequential", lesson_data['display_name'])
        
        # Create an HTML block for lesson content
        html_block_id = self.generate_block_id("html", f"{lesson_data['display_name']}_content")
        html_definition = {
            "_id": ObjectId(),
            "block_type": "html",
            "definition_data": {
                "data": self.sanitize_content(lesson_data['definition_data']),
                "display_name": f"{lesson_data['display_name']} Content"
            }
        }
        
        definition = {
            "_id": definition_id,
            "block_type": "sequential",
            "definition_data": {
                "display_name": lesson_data['display_name']
            }
        }
        
        return {
            "block_id": block_id,
            "definition": definition,
            "html_block": {
                "block_id": html_block_id,
                "definition": html_definition
            },
            "block_type": "sequential",
            "fields": {
                "display_name": lesson_data['display_name'],
                "format": "Lesson"
            }
        }

    def transform_course(self, course_data):
        course_structure = json.loads(course_data['course_structure'])
        blocks = []
        definitions_to_insert = []
        
        # Create course block with new schema
        course_block = {
            "_id": ObjectId(),
            "block_type": "course",
            "fields": {
                "wiki_slug": f"{course_data['display_name'].replace(' ', '')}"
            },
            "edit_info": {
                "edited_by": -1,
                "edited_on": datetime.now(),
                "previous_version": ObjectId(),
                "original_version": ObjectId()
            },
            "schema_version": 1
        }
        
        # Keep existing functionality for modulestore.definitions
        course_definition = {
            "_id": course_block["_id"],
            "block_type": "course",
            "definition_data": {
                "data": self.sanitize_content(course_data['definition_data']),
                "display_name": course_data['display_name'],
                "metadata": {"tabs": [
                    {"type": "courseware", "name": "Course"},
                    {"type": "progress", "name": "Progress"}
                ]}
            }
        }
        definitions_to_insert.append(course_definition)
        
        # Process lessons as before...
        
        return definitions_to_insert, course_block


    def migrate_courses(self):
        """
        Execute the migration process
        """
        cursor = self.mysql_conn.cursor(dictionary=True)
        
        with open('sql/extract.sql', 'r') as file:
            sql_query = file.read()
        
        cursor.execute(sql_query)
        courses = cursor.fetchall()
        
        for course in courses:
            try:
                definitions, structure = self.transform_course(course)
                
                # Insert into MongoDB
                self.definitions.insert_many(definitions)
                self.structures.insert_one(structure)
                print(f"Successfully migrated course: {course['display_name']}")
            except Exception as e:
                print(f"Error migrating course {course['display_name']}: {str(e)}")
        
        cursor.close()
        self.mysql_conn.close()
        self.mongo_client.close()

if __name__ == "__main__":
    # Configuration
    mysql_config = {
        "host": "localhost",
        "user": "root",
        "password": "HBmRC5t8",
        "database": "learndash"
    }
    
    mongo_uri = "mongodb://localhost:27017/"
    
    # Execute migration
    migrator = LearnDashToOpenEdx(mysql_config, mongo_uri)
    migrator.migrate_courses()