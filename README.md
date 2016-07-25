#3 components:
- The actual script (programmatic_venue_update.py)
- The supplemental file, for log-ins and staging vs. prod URLs (suppl.py)
- The bulk upload template (update_venue_template.csv)

#Sys requirement shit:
- Python 3 
- Python module "requests" (I think this comes default with Python3 though)

#User workflow:
1. Edit bulk upload template
2. Save template in same folder as script and supplemental file
3. Edit supplemental file if needed
4. Run "python3 programmatic_venue_update.py update_venue_template.csv" on the c-line
     ---> You can create an alias in your user profile to shorten this

#Notes:
- To minimize work, the user only has to fill in the values in the template that they want changed. If they don't want to change the latitude, for example, they just have to leave it blank.
- During my testing, an HTTP response of 400 was almost always caused by incorrect venue type. It'll be up to Katie and Christian to type in the correct format of the venues. (Subways example that we discussed)
- The script will display the venue names that the user wants to edit before submitting the changes, to allow exiting in case of user-error
- Commas should be avoided when inputting number values
- Columns A and B (Network name and PARTNER vendor ID of venue) and required inputs in the template.
