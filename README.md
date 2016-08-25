#3 components:
- The actual script (programmatic_venue_update.py)
- The supplemental file, for log-ins and staging vs. prod URLs (suppl.py)
- The bulk upload template (update_venue_template.csv)

#Sys requirement shit:

If you have a mac, you probably have python2 installed. This script uses python3. 

The easiest way to install python3 is with Homebrew. If you have Homebrew already, skip down to step 2.

#### 1. Install Homebrew
If you don't have homebrew installed, run this to install it:

`$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

#### 2. Install Python3
Once you have homebrew, run this to install python3:

`$ brew install python3`

#### 3. Install requests Module
The script uses the python requests module. To install it, run this:

`$ pip3 install requests`


#Running the Script

You run the script in your terminal. You need to be in the same directory as the script in order to run it. Steps below:

1. Edit bulk upload template
2. Save template in same folder as script and supplemental file
3. Edit supplemental file if needed (set the url and email and password)
4. Run:
 `$ python3 programmatic_venue_update.py update_venue_template.csv"`
     ---> You can create an alias in your user profile to shorten this



#Notes:
- To minimize work, the user only has to fill in the values in the template that they want changed. If they don't want to change the latitude, for example, they just have to leave it blank.
- During my testing, an HTTP response of 400 was almost always caused by incorrect venue type. It'll be up to Katie and Christian to type in the correct format of the venues. (Subways example that we discussed)
- The script will display the venue names that the user wants to edit before submitting the changes, to allow exiting in case of user-error
- If you attempt to edit a venue that is not yet in the system, this script will ignore it. After script has ran, it will output a .csv of venues that could not be updated.
- Commas should be avoided when inputting number values
- Columns A and B (Network name and PARTNER vendor ID of venue) and required inputs in the template.






