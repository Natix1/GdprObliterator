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

log.info("GDPR Obliterator by natix1")
log.info("Since you are reading this file, you are: ")
log.info("a) Curious")
log.info("b) Debugging")
log.info("If it is the second option, I'm sorry! Please direct any errors to Issues or DM me on discord: natix1, might be curious and check that out")

automateList = None

ExperiencePool = {}
DatastorePool = {}

with open("automation.json", "r") as f:
    automateList = json.load(f)

UID = int(input("Enter user ID to purge: "))
if not UID:
    log.error("No UID entered")
    exit(1)

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

def clearKey(UniverseID: int, dataStoreName: str, keyName: str) -> int:
    clearedKeys = 0
    Experience: rbx.Experience = None
    if UniverseID in ExperiencePool:
        Experience = ExperiencePool[UniverseID]
    else:
        Experience = rbx.Experience(UniverseID, API_KEY)
        ExperiencePool[UniverseID] = Experience
    
    Datastore: rbx.datastore = None
    formatForStore = f"{dataStoreName}_{UniverseID}"
    if formatForStore in DatastorePool:
        Datastore = DatastorePool[formatForStore]
    else:
        Datastore = Experience.get_datastore(dataStoreName)
        DatastorePool[formatForStore] = Datastore

    if not Datastore:
        log.warning(f"Invalid clearKey call, skipping key {keyName} for datastore {dataStoreName} in Universe {UniverseID}")
        return clearedKeys
    
    log.info(f"Clearing key {keyName} in datastore {dataStoreName} in universe {UniverseID}")
    
    if "*" in keyName:
        prefix = keyName.split("*")[0]
        log.info(f"Wildcard detected, listing keys with prefix: {prefix}")
        keys = Datastore.list_keys(prefix)
        
        for key in keys:
            log.info(f"Clearing key {key} in datastore {dataStoreName} in universe {UniverseID}")
            try:
                Datastore.remove_entry(key)
                log.info(f"Clearing key {key} in datastore {dataStoreName} in universe {UniverseID}")
                clearedKeys += 1
            except rbx.exceptions.NotFound:
                log.info(f"Tried deleting invalid key (this is normal): {key}")
        
    else:
        log.info(f"Clearing key {keyName} in datastore {dataStoreName} in universe {UniverseID}")
        try:
            Datastore.remove_entry(keyName)
            clearedKeys += 1
        except rbx.exceptions.NotFound:
            log.info(f"Tried deleting invalid key (this is normal): {keyName}")

    return clearedKeys

totalClears = 0
totalDataStores = 0

for game in automateList:
    gameName: str = game["Name"]
    universeId: int = game["UniverseID"]
    targetDatastores = game["Datastores"]
    print("\n===========\n")
    print(f"Friendly game name: {gameName}")
    print(f"Universe id: {universeId}")

    for datastore in targetDatastores:
        totalDataStores += 1

        dataStoreName = str(datastore["Name"])
        targetDeleteKey = str(datastore["KeyTemplate"].replace("{uid}", str(UID)))
        if "*" in targetDeleteKey:
            partIneed = targetDeleteKey.split("*")[0]
            print(f"All keys that start with {partIneed} inside {dataStoreName}")
        else:     
            print(f"Datastore {dataStoreName} | Target key deletion: {targetDeleteKey}")

    confirmDestructiveAction()

    clearedKeys = 0

    for datastore in targetDatastores:
        dataStoreName = str(datastore["Name"])
        targetDeleteKey = str(datastore["KeyTemplate"].replace("{uid}", str(UID)))
        clearedKeys += clearKey(universeId, dataStoreName, targetDeleteKey)

    print(f"Cleared {clearedKeys} keys in total among {len(targetDatastores)} datastores.")

    totalClears += clearedKeys

Report: str = f"""

\n\n
Clearing done, stats:
Cleared a total of {totalClears} among {totalDataStores},
With a total of {len(automateList)} universes.
\n\n

(The program will now exit)

"""