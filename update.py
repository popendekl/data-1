import pathlib
import os
import os.path
import hashlib
import time

import sheet2csv

SHEET_ID_DEV = "1GDYUsjtJMub8Gh_hZMu4UQw6hAVmtUh6E0rS9dlUl3o"
SHEET_ID_PROD = "1N1qLMoWyi3WFGhIpPFzKsFmVE0IwNP3elb_c18t2DwY"

SHEET_ID = SHEET_ID_PROD

RANGE_STATS = "Podatki!A3:ZZ"
RAGNE_PATIENTS = "Pacienti!A3:ZZ"
RANGE_REGIONS = "Kraji!A1:ZZ"
RANGE_HOSPITALS = "Zdr.sistem!A3:ZZ"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

def sha1sum(fname):
    h = hashlib.sha1()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def key_mapper_kraji(values):
  def clean(x):
    return x.lower().replace(" - ", "-").replace(" ", "_").split('/')[0]
  
  keys = list(map( lambda x: '.'.join(['region', clean(x[0]), clean(x[1])]), zip(values[1][1:], values[0][1:])))
  keys.insert(0, 'date')

  return keys, values[2:]

def import_sheet(update_time, range, filename, **kwargs):
    pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    old_hash = sha1sum(filename)
    try:
        sheet2csv.sheet2csv2(id=SHEET_ID, range=range, api_key=GOOGLE_API_KEY, filename=filename, **kwargs)
    except Exception as e:
        print("Failed to import {}".format(filename))
        raise e
    new_hash = sha1sum(filename)
    if old_hash != new_hash:
        with open("{}.timestamp".format(filename), "w") as f:
            f.write(str(update_time))

if __name__ == "__main__":
    update_time = int(time.time())
    import_sheet(update_time, RANGE_STATS, "csv/stats.csv")
    import_sheet(update_time, RAGNE_PATIENTS, "csv/patients.csv")
    import_sheet(update_time, RANGE_HOSPITALS, "csv/hospitals.csv")
    import_sheet(update_time, RANGE_REGIONS, "csv/regions.csv", rotate=True, key_mapper=key_mapper_kraji, sort_keys=True)