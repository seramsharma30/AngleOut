import os
import json
import re
from urllib.parse import unquote
from app import app
from app.functions import *
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from google.auth.exceptions import RefreshError
from app.routes.gsc_api_auth import *
from flask import render_template, request, url_for, redirect, session
from app.routes.gsc_apis import *
from app.firebase_db import get_keyword_tracker,  get_content_hub_data
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/', methods = ["GET", "POST"])
@app.route('/index', methods = ["GET", "POST"])
@app.route('/home', methods = ["GET", "POST"])
def index():
    return render_template("home.html")

@app.route('/dashboard', methods = ["GET", "POST"])
def dashboard():

    if not session.get("credentials"):
        return redirect(url_for("gsc_authorize"))
    

    try:
        # Retrieve user information and setup form URL
        user_name = session["user_name"]
        user_email = session["user_email"]
        profile_pic = session["profile_pic"]

        # Initialize selected property and date range variables
        selected_property = session.get('selected_property')
        start_date = session.get('start_date')
        end_date = session.get('end_date')
        # site_list_sorted = session.get("site_list_sorted")
        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)

        all_dimensions = {
            "date": ["DATE"],
            "query": ["QUERY"],
            "country": ["COUNTRY"],
            "device": ["DEVICE"],
            "page": ["PAGE"],
            # "all_dimensions_table" : ["QUERY", "PAGE", "COUNTRY", "DEVICE", "DATE"]
            }
        
        if request.method == "POST":
            # Retrieve selected property and date range from form
            selected_property = request.form.get("projects-ids")
            start_date = request.form.get("startDate")
            end_date = request.form.get("endDate")
            
            # Store selected values in session
            session['selected_property'] = selected_property
            session['start_date'] = start_date
            session['end_date'] = end_date


        # If no property is selected, select the first one
        if not selected_property:
            selected_property = site_list_sorted[0]
            session["selected_property"] = selected_property

            # Set the date range
            today = datetime.today()
            start_date = today - timedelta(days=182)
            end_date = today - timedelta(days=2)
            
            start_date, end_date = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            session['start_date'], session["end_date"] = start_date, end_date

        # Fetch data for all dimension from Google Search Console.
        
        tables_data = {}
        today = datetime.today()
        today = today.strftime('%Y-%m-%d')

        for key, value in all_dimensions.items():
            results_df = fetch_search_console_data(webmasters_service = search_console_service, website_url = selected_property,
                                                   start_date=start_date, end_date=end_date, dimensions = value)
            # tables_data[f'{key}_data'] = results_df.to_dict(orient='records')
            tables_data[f'{key}_data'] = results_df.to_dict()


        
        # Convert date DataFrame to calculate metrics
        date_dataframe = pd.DataFrame(tables_data["date_data"])
        click_sum = sum_finder(date_dataframe, 'Clicks')
        impression_sum = sum_finder(date_dataframe, 'Impressions')
        ctr_sum = (date_dataframe["Clicks"].sum() / date_dataframe["Impressions"].sum()) * 100 if date_dataframe["Impressions"].sum() > 0 else 0
        ctr_sum = f"{ctr_sum:.2f}%"
        
        return render_template("dashboard.html", site_list = site_list_sorted, selected_property = selected_property, 
                            start_date = session["start_date"], end_date = session["end_date"], 
                            click_sum = click_sum, ctr_sum = ctr_sum, impression_sum = impression_sum,
                            tables_data = tables_data, user_name = user_name, 
                            profile_pic = profile_pic, user_email = user_email)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        
        return f"""{e}"""

@app.route('/monthlyreport', methods = ["GET", "POST"])
def monthlyreport():

    if not session.get("credentials"):
        return redirect(url_for("gsc_authorize"))
    

    try:    # Retrieve user information and setup form URL
        user_name = session["user_name"]
        user_email = session["user_email"]
        profile_pic = session["profile_pic"]

        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)

        # Initialize selected property and date range variables
        selected_property = session.get('selected_property')
        if not selected_property:
            selected_property = site_list_sorted[0]
            session["selected_property"] = selected_property

        # Today's date
        today = date.today()
        # End date: last day of the previous month
        end_date = date(today.year, today.month, 1) - timedelta(days=1)
        # Start date: 6 months before the start of the previous month
        start_date = (date(today.year, today.month, 1) - relativedelta(months=6))
        # Convert to string format 'yyyy-mm-dd'
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')


        # dates for compare function
        cur_month_end_date = date(today.year, today.month, 1) - relativedelta(days=1)
        cur_month_start_date = date(cur_month_end_date.year, cur_month_end_date.month, 1)

        prev_month_end_date = cur_month_end_date - relativedelta(days=1)
        prev_month_start_date = date(prev_month_end_date.year, prev_month_end_date.month, 1)

        cur_month_end_date = cur_month_end_date.strftime('%Y-%m-%d')
        cur_month_start_date = cur_month_start_date.strftime('%Y-%m-%d')

        prev_month_end_date = prev_month_end_date.strftime('%Y-%m-%d')
        prev_month_start_date = prev_month_start_date.strftime('%Y-%m-%d')




        if request.method == "POST":
            selected_property = request.form.get("projects-ids")
            session['selected_property'] = selected_property

        # Fetch data for date and page dimension from Google Search Console.
        all_dimensions = {
                "date": ["DATE"],
                }

        # print(start_date, end_date)
        tables_data = {}
        for key, value in all_dimensions.items():
            results_df = fetch_search_console_data(search_console_service, selected_property,
                                                    start_date, end_date,
                                                    value)
            tables_data[f'{key}_data'] = results_df.to_dict()
        

        compare_dimensions = {
            "page" : ["PAGE"],
        }
        compare_Dates = {"current_month":(cur_month_start_date, cur_month_end_date), 
                        "previous_month":(prev_month_start_date, prev_month_end_date)}
        compare_tables_data = {}

        for months, dates in compare_Dates.items():

            for key, value in compare_dimensions.items():
                results_df = fetch_search_console_data(search_console_service, selected_property,
                                                    dates[0], dates[1], value)
                compare_tables_data[f'{months}_{key}_data'] = results_df.to_dict()

            
        return render_template("monthlyreport.html", tables_data = tables_data, compare_tables_data = compare_tables_data,
                            site_list_sorted = site_list_sorted, selected_property = selected_property, 
                            user_email = user_email,
                            user_name = user_name, profile_pic = profile_pic)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    
    except Exception as e:
        
        return f"""{e}, {e.__class__.__name__}"""

@app.route('/signout', methods=['GET', 'POST'])
def signout():
    # Clear all session data
    session.pop("credentials", None)
    return redirect(url_for('index'))

@app.route('/ranktracker', methods = ["GET", "POST"])
def ranktracker():
    try:

        if not session.get("credentials"):
            return redirect(url_for("gsc_authorize"))
        

        # Retrieve user information and setup form URL
        user_name = session["user_name"]
        user_email = session["user_email"]
        profile_pic = session["profile_pic"]

        # site_list_sorted = session.get("site_list_sorted")
        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)
        selected_range = session.get('selected_range')
        current_start_date, current_end_date = session.get('current_start_date'), session.get('current_end_date')
        previous_start_date, previous_end_date = session.get('previous_start_date'), session.get('previous_end_date')

        if not current_start_date :
            selected_range = "28"
            session["selected_range"] = selected_range

            today = datetime.today()
            current_start_date = today - timedelta(days=29)
            current_end_date = today - timedelta(days=2)

            previous_start_date = current_start_date - timedelta(days=28)
            previous_end_date = current_start_date - timedelta(days=1)

            current_start_date, current_end_date = current_start_date.strftime('%Y-%m-%d'), current_end_date.strftime('%Y-%m-%d')
            previous_start_date, previous_end_date = previous_start_date.strftime('%Y-%m-%d'), previous_end_date.strftime('%Y-%m-%d')
            session['current_start_date'], session["current_end_date"] = current_start_date, current_end_date
            session['previous_start_date'], session["previous_end_date"] = previous_start_date, previous_end_date
            
            

        # Initialize selected property and date range variables
        selected_property = session.get('selected_property')
        if not selected_property:
            selected_property = site_list_sorted[0]
            session["selected_property"] = selected_property


        if (request.method == "POST") and ('keywords' in request.form):
            keywords = request.form.get('keywords')
            # Add keywords as a single entry to database
            from app.firebase_db import add_keyword_tracker
            add_keyword_tracker(selected_property, user_email, keywords)
            
        elif (request.method == "POST") and ('projects-ids' in request.form or 'date-range' in request.form):
            selected_property = request.form.get("projects-ids")
            session['selected_property'] = selected_property
            selected_range = request.form.get("date-range")
            session['selected_range'] = selected_range

            today = datetime.today()
            if selected_range == "28":
                current_start_date = today - timedelta(days=29)
                current_end_date = today - timedelta(days=2)

                previous_start_date = current_start_date - timedelta(days=28)
                previous_end_date = current_start_date - timedelta(days=1)
            
            elif selected_range == "7":
                current_start_date = today - timedelta(days=8)
                current_end_date = today - timedelta(days=2)

                previous_start_date = current_start_date - timedelta(days=7)
                previous_end_date = current_start_date - timedelta(days=1)
            
            elif selected_range == "90":
                current_start_date = today - timedelta(days=90)
                current_end_date = today - timedelta(days=2)

                previous_start_date = current_start_date - timedelta(days=92)
                previous_end_date = current_start_date - timedelta(days=1)

            current_start_date, current_end_date = current_start_date.strftime('%Y-%m-%d'), current_end_date.strftime('%Y-%m-%d')
            previous_start_date, previous_end_date = previous_start_date.strftime('%Y-%m-%d'), previous_end_date.strftime('%Y-%m-%d')
            session['current_start_date'], session["current_end_date"] = current_start_date, current_end_date
            session['previous_start_date'], session["previous_end_date"] = previous_start_date, previous_end_date

        # Fetch data for date and page dimension from Google Search Console.
        keyword_query = get_keyword_tracker(user_email, selected_property)

        days = {
            "cur" : (current_start_date, current_end_date), 
            "pre" : (previous_start_date, previous_end_date)
            }
        

        if len(keyword_query) == 0:
            return render_template("ranktracked.html", tables_data = None, site_list = site_list_sorted, selected_range = selected_range,
                                site_list_sorted = site_list_sorted, selected_property = selected_property, 
                                user_email = user_email, days = days,
                                user_name = user_name, profile_pic = profile_pic)
        
        keywords = [d['keyword'] for d in keyword_query if d['keyword']]
        all_keys = [k2.strip() for k in keywords for k2 in k.split(',')]
        all_keys = list(set(all_keys))
        
        tables_data = {}
        for keyword_ in all_keys:
            key_ = {}
            for key, value in days.items():
                results_df = fetch_search_console_data_ranktracker(search_console_service, selected_property,
                                                        value[0], value[1], keyword = keyword_)
                key_[key] = results_df.to_dict()
                
            tables_data[keyword_] = key_
        
        # return f"""{tables_data}"""
            
        return render_template("ranktracked.html", tables_data = tables_data, site_list = site_list_sorted, selected_range = selected_range,
                            site_list_sorted = site_list_sorted, selected_property = selected_property, 
                            user_email = user_email, days = days,
                            user_name = user_name, profile_pic = profile_pic)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        return f"""{e}"""
    
@app.route('/contentdecay', methods = ["GET", "POST"])
def contentdecay():
    try :
        if not session.get("credentials"):
            return redirect(url_for("gsc_authorize"))
        
        # Retrieve user information and setup form URL
        user_name = session["user_name"]
        user_email = session["user_email"]
        profile_pic = session["profile_pic"]

        # site_list_sorted = session.get("site_list_sorted")
        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)
        # Initialize selected property and date range variables
        selected_range = session.get('selected_range')
        selected_property = session.get('selected_property')
        if not selected_property:
            selected_property = site_list_sorted[0]
            session["selected_property"] = selected_property
        
        if not selected_range:
            selected_range = 6
            session["selected_range"] = selected_range
            

        

        if request.method == "POST":
            selected_property = request.form.get("projects-ids")
            session['selected_property'] = selected_property
            selected_range = request.form.get("date-range")
            session['selected_range'] = selected_range

        


        # Get today's date
        today = datetime.today()
        # Calculate end_date as the last day of the previous month
        end_date = today.replace(day=1) - relativedelta(days=1)
        # Calculate start_date as the first day of the month 6 months before end_date
        start_date = (end_date.replace(day=1) - relativedelta(months=int(selected_range))).replace(day=1)

        # Format the dates
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')

        all_dimensions = {
                # "date": ["DATE"],
                # "query": ["QUERY"],
                # "country": ["COUNTRY"],
                # "device": ["DEVICE"],
                "page": ["PAGE", "DATE"],
                # "all_dimensions_table" : ["QUERY", "PAGE", "COUNTRY", "DEVICE", "DATE"]
                }
        
        tables_data = fetch_search_console_data(webmasters_service = search_console_service, website_url = selected_property,
                                                start_date=start_date, end_date=end_date, dimensions = ["PAGE", "DATE"]).to_dict()
        
        
        return render_template("contentdecay.html", tables_data = tables_data, site_list = site_list_sorted, selected_range = selected_range,
                            selected_property  = selected_property , user_email = user_email,
                            user_name = user_name, profile_pic = profile_pic)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        return f"""{e}"""

@app.route('/contenthub', methods = ["GET", "POST"])
def contenthub():
    try:
        if not session.get("credentials"):
            return redirect(url_for("gsc_authorize"))
        
        # Retrieve user information and setup form URL
        user_name = session["user_name"]
        user_email = session["user_email"]
        profile_pic = session["profile_pic"]
        # site_list_sorted = session.get("site_list_sorted")
        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)
        selected_property = session.get('selected_property')
        if not selected_property:
            selected_property = site_list_sorted[0]
            session["selected_property"] = selected_property
        
        if (request.method == "POST") and ('projects-ids' in request.form):
            selected_property = request.form.get("projects-ids")
            session['selected_property'] = selected_property


        content_hub_data = get_content_hub_data(user_email, selected_property)

        # return f"""{content_hub_data}"""

        return render_template("contenthub.html", site_list = site_list_sorted,
                            site_list_sorted = site_list_sorted, selected_property = selected_property, 
                            user_email = user_email, content_hub_data = content_hub_data,
                            user_name = user_name, profile_pic = profile_pic)
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        return f"""{e}"""

@app.route('/keywordvault', methods = ["GET", "POST"])
def keywordvault():

    try :
        if 'credentials' not in session:
            return redirect(url_for("gsc_authorize"))
        
        user_name = session.get("user_name")
        user_email = session.get("user_email")
        profile_pic = session.get("profile_pic")

        search_console_service = build_gsc_service()
        site_list_sorted = get_site_urls(search_console_service)

        selected_property = session.get('selected_property')

        if not selected_property:
            selected_property = site_list_sorted[0]
            session['selected_property'] = selected_property
        
        if request.method == "POST":
            selected_property = request.form.get("projects-ids")
            session['selected_property'] = selected_property
        
        today = datetime.today()
        start_date = today - timedelta(days=29)
        end_date = today - timedelta(days=2)
        start_date, end_date = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

        
        results_df = fetch_search_console_data_keyword_valut(webmasters_service = search_console_service, website_url = selected_property,
                                                start_date=start_date, end_date=end_date, dimensions = ["PAGE"])
            
        results_df = results_df.to_dict()
        # return f"""{results_df}"""
        return render_template("keyword_vault.html", results_df  = results_df, site_list = site_list_sorted, selected_property = selected_property,
                            user_email = user_email, user_name = user_name, profile_pic = profile_pic)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    # except Exception as e:
    #     return f"""{e}"""


@app.route('/keywordvault/urls/<path:urls_>', methods = ["GET", "POST"])
def keywordvault_urls(urls_):

    try:
        if 'credentials' not in session:
            return redirect(url_for("gsc_authorize"))
        decoded_url = unquote(urls_)
        
        user_name = session.get("user_name")
        user_email = session.get("user_email")
        profile_pic = session.get("profile_pic")
        search_console_service = build_gsc_service()
        
        if request.method == "POST":
            keyword_type = request.form.get("keyword-type")
            session['keyword_type'] = keyword_type

        today = datetime.today()
        start_date = today - timedelta(days=29)
        end_date = today - timedelta(days=2)
        start_date, end_date = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

        results_df = fetch_search_console_data_keyword_display(webmasters_service = search_console_service, website_url = session.get('selected_property'),
                                                start_date=start_date, end_date=end_date, url = decoded_url)
            
        results_df = results_df.to_dict()
        # return f"""{results_df}"""

        return render_template("keyword_display.html", results_df  = results_df, url = decoded_url,
                            user_email = user_email, user_name = user_name, profile_pic = profile_pic)
    
    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        return f"""{e}"""

@app.route('/schema_generator', methods = ["GET", "POST"])
def schema_generator():
    try:
        if 'credentials' not in session:
            return redirect(url_for("gsc_authorize"))
        
        user_name = session.get("user_name")
        user_email = session.get("user_email")
        profile_pic = session.get("profile_pic")
        url = session.get('url', None)
        schema_type = session.get('schema_type', None)
        response = session.get('response', None)

        prompt = '''You are an SEO expert. I will provide you with a website URL {url} and a schema type {schema_type}.
        
        Your task is to:
        1. Analyze the content of the website.
        2. Generate a valid JSON-LD structured data snippet using the given schema type.

        Important rules:
        - Use only information that is explicitly available on the website.
        - Do not invent, assume, or hallucinate any data (e.g., reviews, ratings, prices, SKUs, availability, brand, etc.).
        - If a field is present on the website, include it. If it is missing, omit it.
        - Strive to include all available relevant fields for the given schema type based on the content found.
        - Output only the raw JSON-LD code.
        - Do not include any explanation, markdown, triple backticks, or additional characters.
        - The output must be valid and suitable for SEO and compliant with schema.org standards.

        '''

        if request.method == "POST":
            url = request.form.get("url")
            schema_type = request.form.get("schema_type")
            session['url'] = url
            session['schema_type'] = schema_type

        if url and schema_type:
            prompt = prompt.format(url = url, schema_type = schema_type)
            response = client.responses.create(
                model="gpt-4.1",
                input=prompt,
                temperature=0
                )
            response = json.loads(response.output[0].content[0].text)
            session['response'] = response

        return render_template("schema_gen.html", user_name = user_name, user_email = user_email, profile_pic = profile_pic,
                               url = url, schema_type = schema_type, response = response)
    


    except RefreshError:
        return redirect(url_for("gsc_authorize"))
    except Exception as e:
        return f"""{e}"""
