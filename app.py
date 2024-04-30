from dotenv import load_dotenv
load_dotenv()  # Loading all environment variables

import streamlit as st
import os
import pymysql
import google.generativeai as genai
import pandas as pd

# Configuring API key
GOOGLE_API_KEY = "AIzaSyC8VSPGQu2pyXz0vMHVoFTCMmFMBJ7nXPk"
genai.configure(api_key=GOOGLE_API_KEY)

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    cleaned_response = clean_sql_query(response.text)
    return cleaned_response

def clean_sql_query(sql_query):
    # Remove triple backticks and additional characters
    cleaned_query = sql_query.replace('```sql\n', '').replace('```', '').strip()
    return cleaned_query

# Function to retrieve data from the database using the query
def read_sql_query(sql, db):
    DB_HOST = "tr-wp-database.cfqdq6ohjn0p.us-east-1.rds.amazonaws.com"
    DB_USER = "riya"
    DB_PASSWORD = "Trailytics@789"
    DB_DATABASE =   "Abbott"
    DB_PORT = 3306
    
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        db=DB_DATABASE,
        port=DB_PORT,
        connect_timeout=1000,
        autocommit=True
    )

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    connection.commit()
    connection.close()
    return rows

# Defining the prompt
prompt = ["""Train a model to understand and execute SQL queries related to product data retrieval from various e-commerce platforms. The goal is to extract information from flipkart_crawl_pdp and the names of the columns in flipkart_crawl_pdp. The names of the columns are pdp_crawl_data_id,pf_id,crawl_id,sku_id,web_pid,pdp_title_value,brand_id,brand_name,price_rp,price_sp,pdp_rating_value,pdp_review_count,pdp_rating_count,pdp_qa_count,pdp_desc_value,pdp_image_count,pdp_image_url,pdp_image_url_all,osa,pdp_page_url,pdp_discount_value,pdp_bulletin_value,pdp_number_of_bulletin,ec_number_of_images,reseller_name_crawl,seller_rank,five_star,four_star,three_star,two_star,one_star,location_id,location_name,created_by,created_on,modified_by,modified_on,status,pincode,extracted_brand_name,ec_number_of_videos,osa_remark,delivery_date,deal_flag,pdp_top_review,msl
"
ok and you also have to add a AND statment in the end of every query if someone like for amazon the below statement the mapping of these pf_id are as 1:amazon,2:flipkart,3:nykaa,4:myntra,5:meesho
Sample queries and queries for reference are:

          1.	Find those products which have 0 image count.
Select * from rb_pdp where date(created_on) = date(now())-1 and pdp_image_count = 0;
2.	Find those products which have been OOS for a week .
SELECT pf_id, pincode, web_pid, pdp_title_value, pdp_page_url
FROM (
  SELECT pf_id, pincode, web_pid, DATE(created_on), osa, pdp_title_value, pdp_page_url,
         ROW_NUMBER() OVER (PARTITION BY pf_id, pincode, web_pid ORDER BY DATE(created_on) DESC) AS rn
  FROM rb_pdp
  WHERE osa = 0 AND DATE(created_on) >= DATE_SUB(CURRENT_DATE()-1, INTERVAL 7 DAY)
) subquery
WHERE rn = 7 AND pf_id = 1;

3.	Find those products whose seller name is None.
Select * from rb_pdp where date(created_on) = date(now())-1 and reseller_name_crawl is None;

4.	Find products which have blank description value.
Select * from rb_pdp where date(created_on) = date(now())-1 and pdp_desc_value is None;

5.	Find latest date of reviews for Amazon
SELECT * FROM rb_crawl_review_info WHERE pf_id = 1 ORDER BY created_time DESC;


6.	Find those products which have lowest availability on each platform.
SELECT pf_id,pincode,SUM(osa)/COUNT(*) FROM rb_pdp WHERE DATE(created_on)=DATE(NOW()) GROUP BY pf_id,pincode;

7.	Find list of those products which have more than 30% discount.
Select * from rb_pdp where date(created_on) = date(now())-1 and price_variation > 30;

ok and you also have to add a AND statment in the end of every query if someone like for amazon the below statement the mapping of these pf_id are as 1:amazon,2:flipkart,3:nykaa,4:myntra,5:meesho
8.	Find list of those products which have more than 30% discount.
Select * from rb_pdp where date(created_on) = date(now())-1 and price_variation > 30 and pf_id=1;

9.if someone give me oos for a particular day or simply write give oos/out of stock .
select * from rb_pdp where date(created_on) = date(now()) and pf_id=2 if someome says 3 days old then select * from rb_pdp where date(created_on) = date(now())-3
w
Ensure the model can comprehend and execute queries with the `DATE()` and `CURDATE()` functions, and handle variations in table and column names for different e-commerce platforms should not contain triple backticks in the beginning or end.\n
           also, the SQL code should not have ``` in the beginning or end and SQL word in output
    """]

# Streamlit app
st.header("Trailytics Data Retrieval")

# Input query using Streamlit text_area
question = st.text_area("Input your question here:")

# If submit is clicked
if st.button("Submit"):
    response = get_gemini_response(question, prompt)
    cleaned_query = clean_sql_query(response)
    print(cleaned_query)
    rows = read_sql_query(cleaned_query, "abc.db")

    st.subheader("The Response is")

    # Convert rows to DataFrame
    df = pd.DataFrame(rows)

    # Display the DataFrame
    st.dataframe(df)
