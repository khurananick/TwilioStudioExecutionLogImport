**Please note this is not an official Twilio supported application.**\
**This application does not come with any warranties. You may use this application at your own risk.** 

## Intro
Use this app to import your studio logs into Elasticsearch and display using Kibana.

## Setup
**Step 1:** Ensure Elasticsearch and Kibana are installed an running on your machine. For mac users, download and install with:

- `brew install elasticsearch-full`
- `brew install kibana-full`

Once installed, make sure the services are running:

- `brew services start elasticsearch-full`
- `brew services start kibana-full`

Confirm both services are running.

**Elastisearch** defaults to: `localhost:9200`\
**Kibana** defaults to: `localhost:5601`

**Step 2:** Clone this repo to your machine.

**Step 3:** Create a .env file and add `ACCOUNT_SID` and `AUTH_TOKEN` from your Twilio account.

**Step 4:** Run `pip3 install -r requirements.txt` to download required libs.

**Step 5:** Edit your Kibana dashboard with the widgets that fit your output.
- For a **Tree Graph**, use the `tree.json` data and plug into a Vega visualizer in your Kibana dashboard.

## How To Test
**Testing Requirements**
- This library will test against data in your Twilio project for which you enter your credentails into the secret.py file.
- Make sure you have run your flow at least once within the last 24 hours for this test to work.
- Once you have created a flow and ran it at least once, copy the SID of your flow and run the test as follows: 

`python3 test.py {FLOW_SID}`


## How To Run

`python3 run.py {FLOW_SID}`

- This will start the import.

