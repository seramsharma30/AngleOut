import os
import re
from app import app

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from app.routes.gsc_api_auth import *
from flask import render_template, request, url_for, redirect, session, jsonify
from app.routes.gsc_apis import *
from app.firebase_db import add_content_hub_data, delete_content_hub_data, update_content_hub_data


@app.route('/add_new_content', methods=["POST"])
def add_new_content():
    if request.method == "POST":
        
        try:    
            # Add the data to Firebase
            result = add_content_hub_data(
                user_gmail=session.get('user_email'),
                site_url=session.get('selected_property'),
                PRIORITY=request.form.get('PRIORITY'),
                NAME=request.form.get('NAME'),
                BRIEF=request.form.get('BRIEF'),
                PRIMARY_KEYWORD=request.form.get('PRIMARY KEYWORD'),
                FUNNEL_STAGE=request.form.get('FUNNEL STAGE'),
                STATUS=request.form.get('STATUS'),
                LIVE_URL=request.form.get('LIVE URL'),
                LAST_UPDATED=request.form.get('LAST UPDATED'),
            )
            
            if result:
                return redirect(url_for('contenthub'))
            else:
                return jsonify({'error': 'Failed to add content'}), 500
                
        except Exception as e:
            print(f"Error adding content: {str(e)}")
            return jsonify({'error': str(e)}), 500
        

@app.route('/delete_content', methods=["POST"])
def delete_content():
    if request.method == "POST":
        try:
            id = request.form.get('id')
            result = delete_content_hub_data(id, session.get('user_email'))
            if result:
                return redirect(url_for('contenthub'))
            else:
                return jsonify({'error': 'Failed to delete content'}), 500
        except Exception as e:
            print(f"Error deleting content: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
@app.route('/update_content', methods=["POST"])
def update_content():
    if request.method == "POST":
        
        try:    
            # update the data to Firebase
            result = update_content_hub_data(
                user_gmail=session.get('user_email'),
                site_url=session.get('selected_property'),
                PRIORITY=request.form.get('PRIORITY'),
                NAME=request.form.get('NAME'),
                BRIEF=request.form.get('BRIEF'),
                PRIMARY_KEYWORD=request.form.get('PRIMARY KEYWORD'),
                FUNNEL_STAGE=request.form.get('FUNNEL STAGE'),
                STATUS=request.form.get('STATUS'),
                LIVE_URL=request.form.get('LIVE URL'),
                LAST_UPDATED=request.form.get('LAST UPDATED'),
                doc_id=request.form.get('id')
            )
            
            if result:
                return redirect(url_for('contenthub'))
            else:
                return jsonify({'error': 'Failed to update content'}), 500
                
        except Exception as e:
            print(f"Error updating content: {str(e)}")
            return jsonify({'error': str(e)}), 500
