import csv 

from nautobot.core.jobs import Job, BooleanVar, FileVar, ObjectVar
from nautobot.dcim.models import Location, LocationType
from nautobot.extras.models import Status

from state_abbreviations import us_state_abbreviations

name = "CSV Locations"

class CSVImportJob(Job):
    """Job to import locations from a CSV file."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_results = {
            "created": 0,
            "errors": 0,
        }
        self.us_state_abbreviations = us_state_abbreviations


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
        
        csv_reader = csv.DictReader(csv_file)
        row_count = 1

        for row in csv_reader:
            site_name = row.get("name", "")
            state_name = row.get("state", "")
            city_name = row.get("city", "")
            site_type = self.parse_site_type(site_name)

            # convert state name to full name

            if self.us_state_abbreviations.get(state_name):
                state_name = self.us_state_abbreviations[state_name]

            state, _ = Location.objects.get_or_create(
                name=state_name,
                status=self.location_status,
                type=LocationType.objects.get(name="State"),
            )
            city, _ = Location.objects.get_or_create(
                name=city_name,
                status=self.location_status,
                type=LocationType.objects.get(name="City"),
                parent=state,
            )
            site, _ = Location.objects.get_or_create(
                name=site_name,
                status=self.location_status,
                type=LocationType.objects.get(name=site_type),
                parent=city,
            )
            row_count += 1
            self.job_results["created"] += 1
        return self.job_results


        
