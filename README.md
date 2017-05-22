#3 components:
- The actual script (venue_create_edit.py)
- The supplemental file, for log-ins and staging vs. prod URLs (suppl.py)
- The bulk upload template (template.csv)

#Sys requirement shit:

If you have a mac, you probably have python2 installed. This script uses python3. 

The easiest way to install python3 is with Homebrew. If you have Homebrew already, skip down to step 2.

#### 1. Install Homebrew
If you don't have homebrew installed, run this to install it:

`$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

#### 2. Install Python3
Once you have homebrew, run this to install python3:

`$ brew install python3`

#### 3. Install requests and pandas Module
The script uses the pandas and requests modules. To install them, run:

`$ pip3 install requests`
`$ pip3 install pandas`


#Running the Script

You run the script in your terminal. You need to be in the same directory as the script in order to run it. Steps below:

1. Edit bulk upload template. IMPORTANT: Make sure venues naming format is identical to how the venues appear in our dashboard.
2. Save template in same folder as script and supplemental file
3. Edit supplemental file if needed (set the url and email and password)
4. Run:


 `$ python3 venue_create_edit.py e template.csv"`
     ---> This runs an EDIT (aka UPDATE) job

    or:

`$ python3 venue_create_edit.py c template.csv"`
     ---> This runs a CREATION job

    or:

`$ python3 venue_create_edit.py d template.csv"`
     ---> This runs a DELETION job


#Notes:

- The template uses row 2 to inform you which cells are required for creation. Please overwrite this row with a venue or delete it.
- For deleting: ONLY fill in the first two columns. No other data is necessary. Before deletion is processed, a CSV will be outputted in case of accidental deletion.
- For editing: To minimize work, the user only has to fill in the values in the template that they want changed. If they don't want to change the latitude, for example, they just have to leave it blank.
- To exclude a buy type, simply fill in the appropriate cell with any value (eg. 'x'). Otherwise, leave blank.
- For editing: If you attempt to edit a venue that is not yet in the system, this script will ignore it. After script has ran, it will output a .csv of venues that could not be updated.
- Commas should be avoided when inputting number values
- Don't add columns!
- Common causes of a 400 error: Incorrectly formatted venue; typos; unknown adjustments to the API made by devs