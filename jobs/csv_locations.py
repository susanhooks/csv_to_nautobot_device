import csv 
from io import StringIO

from nautobot.core.jobs import Job, BooleanVar, FileVar, ObjectVar
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status


STATE_ABBREVIATIONS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FM": "Federated States of Micronesia",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "MP": "Northern Mariana Islands",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PW": "Palau",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VI": "Virgin Islands",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",

}

name = "CSV Locations"

class CSVImportJob(Job):
    """Job to import locations from a CSV file."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_results = {
            "created": 0,
            "errors": 0,
        }


    class Meta:
        """Job metadata."""

        name = "CSV Import Locations"
        description = "Import locations from a CSV file"
    
    debug = BooleanVar(description="Enable debug mode", default=False)

    csv_file = FileVar(description="CSV file containing locations to import")

    location_status = ObjectVar(model=Status, query_params={"content_types": "dcim.location"})

    def parse_site_type(self, site_name):
        site_type_map = {
            "DC": "Data Center",
            "BR": "Branch",
        }

        split_name = site_name.split("-")

        site_type_abbr = split_name[1] if len(split_name) > 1 else ""

        return site_type_map.get(site_type_abbr, "Data Center")

    def run(self, csv_file, debug, location_status, *args, **kwargs):
        """Run the job."""
        self.debug = debug
        self.csv_file = csv_file
        self.location_status = location_status

        decoded_csv_file = csv_file.read().decode("utf-8")
        csv_reader = csv.DictReader(StringIO(decoded_csv_file)) 
        
        row_count = 1

        for row in csv_reader:
            site_name = row.get("name", "")
            state_name = row.get("state", "")
            city_name = row.get("city", "")
            site_type = self.parse_site_type(site_name)

            # convert state name to full name

            if STATE_ABBREVIATIONS.get(state_name):
                state_name = STATE_ABBREVIATIONS[state_name]

            state, _ = Location.objects.get_or_create(
                name=state_name,
                status=self.location_status,
                location_type=LocationType.objects.get(name="State"),
            )
            city, _ = Location.objects.get_or_create(
                name=city_name,
                status=self.location_status,
                location_type=LocationType.objects.get(name="City"),
                parent=state,
            )
            site, _ = Location.objects.get_or_create(
                name=site_name,
                status=self.location_status,
                location_type=LocationType.objects.get(name=site_type),
                parent=city,
            )
            row_count += 1
            self.job_results["created"] += 1
        return self.job_results


        
