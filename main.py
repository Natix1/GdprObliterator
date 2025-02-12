import os
import logging
import json
import rblxopencloud as rbx
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)
logging.basicConfig(filename="latest.log", encoding="utf-8", level=logging.DEBUG, filemode="w")
API_KEY: str = os.environ.get("OPEN_CLOUD_KEY")

if not API_KEY:
    log.error("Please define an API key in an .env file, name is OPEN_CLOUD_KEY")
    exit(1)
else:
    log.debug("Found OPEN_CLOUD_KEY environment variable")

automateList = None
with open("automation.json", "r") as f:
    automateList = json.load(f)

UID = 1862042823

def confirmDestructiveAction():
    print("The above action is destructive, meaning it has irreversible consequences. Are you 100% certain? y(es)/n(o)", end=" ")
    try:
        choice = input().lower()
    except KeyboardInterrupt:
        print("\nCtrl+C, aborting safely...")
        log.info("Aborted by keyboard interrupt.")
        exit(0)

    if choice == "n" or choice == "no":
        log.info("Aborted by user.")
        exit(0)
    elif choice == "y" or choice == "ye" or choice == "yes":
        return
    else:
        log.critical("Invalid choice: " + choice)
        exit(1)

def clearKey(UniverseID: int, dataStoreName: str, keyName: str):
    Experience = rbx.Experience(UniverseID, API_KEY)
    Datastore = Experience.get_datastore(dataStoreName)
    if not Datastore:
        log.warning(f"Invalid clearKey call, skipping key {keyName} for datastore {dataStoreName} in Universe {UniverseID}")
        return
    
    log.info(f"Clearing key {keyName} in datastore {dataStoreName} in universe {UniverseID}")
    Datastore.remove_entry(keyName)

for game in automateList:
    gameName: str = game["Name"]
    universeId: int = game["UniverseID"]
    targetDatastores = game["Datastores"]
    print(f"Friendly game name: {gameName}")
    print(f"Universe id: {universeId}")

    for datastore in targetDatastores:
        dataStoreName = str(datastore["Name"])
        targetDeleteKey = str(datastore["KeyTemplate"].replace("{uid}", str(UID)))
        print(f"Datastore {dataStoreName} | Target key deletion: {targetDeleteKey}")
        
    confirmDestructiveAction()

    clearedKeys = 0

    for datastore in targetDatastores:
        dataStoreName = str(datastore["Name"])
        targetDeleteKey = str(datastore["KeyTemplate"].replace("{uid}", str(UID)))
        clearKey(universeId, dataStoreName, targetDeleteKey)
        clearedKeys += 1

    print(f"Cleared {clearedKeys} keys in total among {len(targetDatastores)} datastores in a total of {len(automateList)} universes.")